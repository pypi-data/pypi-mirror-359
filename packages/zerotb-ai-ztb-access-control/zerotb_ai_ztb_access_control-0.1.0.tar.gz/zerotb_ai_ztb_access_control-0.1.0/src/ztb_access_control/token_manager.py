"""
Cognito JWT token utilities for ZTB Access Control
"""
import base64
import json
from typing import Dict, Any
from .exceptions import InvalidToken, ServiceException, RuntimeException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends, HTTPBearer, Request
import jwt
import httpx
import logging
import traceback
from config import settings

security = HTTPBearer()

class TokenManager:
    """Cognito JWT token manager"""
    
    def __init__(self):
        """Initialize token manager for Cognito tokens"""
        pass
    async def verify_token(self, token: str) -> dict:
        """Verify a Cognito token and return the decoded payload."""
        if not token:
            raise ValueError("Token is required.")

        # Fetch Cognito public keys
        keys_url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(keys_url)
                response.raise_for_status()
                keys = response.json()["keys"]
        except httpx.RequestError as e:
            logging.error(f"Failed to fetch Cognito public keys: {str(e)}")
            raise ServiceException("Failed to verify token.")
        # Decode the token header to get the key ID (kid)
        try:
            header = jwt.get_unverified_header(token)
            kid = header["kid"]

        except jwt.PyJWTError as e:
            raise RuntimeError(f"Failed to decode token header: {str(e)}")

        # Find the matching public key
        key = next((k for k in keys if k["kid"] == kid), None)
        if not key:
            raise RuntimeError("Public key not found for the provided token.")

        # Construct the public key
        public_key = jwt.api_jwk.PyJWK.from_json(json.dumps(key)).key

        # Verify and decode the token
        try:
            alg = header.get("alg", settings.JWT_ALGORITHM)

            decoded_token = jwt.decode(
                token,
                public_key,
                algorithms=[alg],  # Use the algorithm from the token header
                options={"verify_aud": False},
                issuer=f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}",
            )

            return decoded_token
        except jwt.ExpiredSignatureError:
            raise RuntimeError("Token has expired.")
        except jwt.InvalidTokenError as e:
            raise RuntimeError(f"Invalid token: {str(e)}")
        except Exception as e:
            logging.error(
                f"Unexpected error while fetching Cognito public keys: {traceback.format_exc()}"
            )
        raise RuntimeException("An unexpected error occurred while verifying token.")
    
    async def get_current_user(self,credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """Dependency to get the current user from the token."""
        token = credentials.credentials
        if not token:
            raise HTTPException(status_code=401, detail="No token provided")
    
        try:
            decoded = await self.verify_token(token)
            if not decoded:
                raise InvalidToken()
            return decoded
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
    
    def decode_cognito_token(self, token: str) -> Dict[str, Any]:
        """Decode Cognito JWT token"""
        try:
            # Split the token
            _, payload, _ = token.split('.')
            
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            
            # Decode the payload
            decoded_payload = base64.urlsafe_b64decode(payload)
            return json.loads(decoded_payload)
        except Exception as e:
            raise InvalidToken(f"Invalid token format: {str(e)}")
    
    def _extract_token_context(self,user: dict):
        """Extract context from JWT token claims"""
        return {
            'user_id': user.get('sub'),
            'tenant_id': user.get('tenant_id') or user.get('tenant_id'),
            'org_id': user.get('organization_id') or user.get('organization_id'),
            'request_scope': user.get('request_scope') or user.get('scope', 'list_tenants'),
            'email': user.get('email'),
            'token_exp': user.get('exp'),
            'token_iat': user.get('iat')
        }
    
    
    def _extract_resource_context(self, request: Request):
        """Extract resource context from request"""
        path_params = request.path_params
        query_params = dict(request.query_params)
        
        return {
            'tenant_id': path_params.get('tenant_id'),
            'org_id': path_params.get('org_id') or path_params.get('organization_id'),
            'resource_id': path_params.get('id') or path_params.get('user_id') or path_params.get('resource_id') or "default",
            'query_params': query_params,
            'path': request.url.path
        }

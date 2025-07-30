"""
FastAPI dependencies for ZTB Access Control - Lightweight permission checking only
"""
from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth_client import AuthClient
from .models import AuthContext
from .exceptions import AuthException, InvalidToken, PermissionDenied, InsufficientScope
from .config import AuthConfig
from token_manager import TokenManager

# Global auth client instance
_auth_client: Optional[AuthClient] = None

security = HTTPBearer()
token_m= TokenManager()

# Constants
INVALID_USER_CONTEXT = "Invalid user context"
USER_ID_NOT_FOUND = "User ID not found in token"
PERMISSION_CHECK_FAILED = "Permission check failed"

def init_auth_client(config: AuthConfig):
    """Initialize the global auth client"""
    global _auth_client
    _auth_client = AuthClient(config)


def get_auth_client() -> AuthClient:
    """Get the auth client instance"""
    if _auth_client is None:
        raise HTTPException(
            status_code=500,
            detail="Auth client not initialized. Call init_auth_client() first."
        )
    return _auth_client


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_client: AuthClient = Depends(get_auth_client)
) -> AuthContext:
    """
    FastAPI dependency to get current authenticated user from Cognito token
    """
    try:
        token = credentials.credentials
        auth_context = auth_client.authenticate_token(token)
        return auth_context
    except InvalidToken as e:
        raise HTTPException(status_code=401, detail=str(e))
    except AuthException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


def require_permission(resource: str, action: str):
    """
    FastAPI dependency factory to require specific permission
    
    Usage:
    @app.get("/api/v1/organizations")
    async def list_organizations(
        user: AuthContext = Depends(get_current_user),
        _: bool = Depends(require_permission("organization", "list"))
    ):
        return {"organizations": []}
    """
    async def permission_dependency(
        request: Request,
        auth_context: AuthContext = Depends(get_current_user),
        auth_client: AuthClient = Depends(get_auth_client)
    ) -> bool:
        try:
            # Validate scope access first
            endpoint_path = request.url.path
            if not _validate_scope_access(auth_context.request_scope.value, endpoint_path):
                raise HTTPException(
                    status_code=403,
                    detail=f"Scope '{auth_context.request_scope.value}' insufficient for this operation"
                )
            
            result = await auth_client.check_permission(
                auth_context=auth_context,
                resource=resource,
                action=action
            )
            
            if not result.allowed:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {result.reason or 'Insufficient privileges'}"
                )
            
            return True
            
        except PermissionDenied as e:
            raise HTTPException(status_code=403, detail=str(e))
        except InsufficientScope as e:
            raise HTTPException(status_code=403, detail=str(e))
        except AuthException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Permission check error: {str(e)}")
    
    return permission_dependency

def _validate_user_context(user: dict) -> str:
    """Validate user context and return user ID"""
    if not isinstance(user, dict):
        raise HTTPException(status_code=401, detail=INVALID_USER_CONTEXT)
    
    username = user.get('sub')
    if not username:
        raise HTTPException(status_code=401, detail=USER_ID_NOT_FOUND)
    
    return username

def _validate_scope_access(request_scope: str, endpoint_path: str) -> bool:
    """Validate if the request scope allows access to the endpoint"""
    
    # Scope hierarchy and access rules
    scope_rules = {
        'list_tenants': {
            'allowed_endpoints': ['/tenants', '/auth/select-tenant', '/users/select-tenant'],
            'allowed_methods': ['GET', 'POST']
        },
        'list_organizations': {
            'allowed_endpoints': ['/organizations', '/auth/select-organization', '/users/select-organization'],
            'allowed_methods': ['GET', 'POST']  
        },
        'unrestricted': {
            'allowed_endpoints': ['*'],  # Access to all endpoints
            'allowed_methods': ['*']
        }
    }
    
    # Check if scope exists
    if request_scope not in scope_rules:
        return False
    
    # Unrestricted scope allows everything
    if request_scope == 'unrestricted':
        return True
    
    # Check specific scope rules
    scope_config = scope_rules[request_scope]
    allowed_endpoints = scope_config['allowed_endpoints']
    
    # Check if endpoint is allowed for this scope
    for allowed_endpoint in allowed_endpoints:
        if allowed_endpoint == '*' or allowed_endpoint in endpoint_path:
            return True
    
    return False


def require_scope(required_scope: str):
    """
    FastAPI dependency factory to require specific token scope
    """
    def scope_dependency(
        auth_context: AuthContext = Depends(get_current_user)
    ) -> bool:
        if auth_context.request_scope.value != required_scope:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient scope. Required: {required_scope}, Got: {auth_context.request_scope.value}"
            )
        return True
    
    return scope_dependency

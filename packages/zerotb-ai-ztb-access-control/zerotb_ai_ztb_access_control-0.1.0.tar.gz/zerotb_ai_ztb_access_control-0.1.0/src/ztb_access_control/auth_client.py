from typing import Optional, Dict, Any
from .config import AuthConfig
from .cerbos_client import CerbosManager
from .token_manager import TokenManager
from .models import (
    AuthContext, PermissionResponse
)


class AuthClient:
    """Lightweight authentication and authorization client - Cerbos only"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.cerbos = CerbosManager(config.cerbos_host, config.cerbos_tls)
        self.token_manager = TokenManager()
        self._initialized = False
    
    def initialize(self):
        """Initialize the auth client"""
        if not self._initialized:
            self._initialized = True
    
    def close(self):
        """Close the auth client"""
        pass
    
    def authenticate_token(self, token: str) -> AuthContext:
        """Extract auth context from Cognito token"""
        self.initialize()
        
        # Extract auth context from Cognito token
        auth_context = self.token_manager._extract_token_context(token)
        
        return auth_context
    
    async def check_permission(
        self,
        auth_context: AuthContext,
        resource: str,
        action: str,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PermissionResponse:
        """Check if user has permission for action on resource"""
        self.initialize()
        
        # # Check scope first
        # if not self._check_scope_permission(auth_context, resource, action):
        #     return PermissionResponse(
        #         allowed=False,
        #         reason="Insufficient token scope",
        #         metadata={"required_scope": "unrestricted"}
        #     )
        
        # Use Cerbos for detailed permission check
        return await self.cerbos.check_permission(
            auth_context, resource, action, resource_id, context
        )
    
    def _check_scope_permission(
        self,
        auth_context: AuthContext,
        resource: str,
        action: str
    ) -> bool:
        """Check if token scope allows the action"""
        scope = auth_context.request_scope.value
        
        if scope == self.config.unrestricted_scope:
            return True
        elif scope == self.config.list_tenants_scope:
            return resource == "tenant" and action == "list"
        elif scope == self.config.list_orgs_scope:
            return resource in ["tenant", "organization"] and action in ["list", "read"]
        
        return False

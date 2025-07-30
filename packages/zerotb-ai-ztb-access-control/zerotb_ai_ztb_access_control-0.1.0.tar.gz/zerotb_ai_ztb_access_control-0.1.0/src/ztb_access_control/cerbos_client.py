"""
Cerbos client integration for ZTB Access Control
"""
from typing import Dict, Any, List, Optional
from .models import PermissionResponse, AuthContext

try:
    from cerbos.sdk.client import CerbosClient
    from cerbos.sdk.model import Principal, Resource, CheckResourcesRequest
except ImportError:
    # Fallback for development
    class CerbosClient:
        def __init__(self, *args, **kwargs):
            pass
    
    class Principal:
        def __init__(self, *args, **kwargs):
            pass
    
    class Resource:
        def __init__(self, *args, **kwargs):
            pass
    
    class CheckResourcesRequest:
        def __init__(self, *args, **kwargs):
            pass


class CerbosManager:
    """Cerbos client manager for RBAC/ABAC"""
    
    def __init__(self, host: str, tls: bool = False):
        self.host = host
        self.tls = tls
        self._client = None
    
    def _get_client(self) -> CerbosClient:
        """Get Cerbos client instance"""
        if not self._client:
            if self.tls:
                self._client = CerbosClient(f"https://{self.host}")
            else:
                self._client = CerbosClient(f"http://{self.host}")
        return self._client
    
    async def check_permission(
        self,
        auth_context: AuthContext,
        resource: str,
        action: str,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PermissionResponse:
        """Check permission using Cerbos"""
        client = self._get_client()
        
        # Build principal
        principal_id = auth_context.user_id
        principal_roles = auth_context.roles
        principal_attrs = {
            "tenant_id": auth_context.tenant_id,
            "organization_id": auth_context.organization_id,
        }
        
        if context:
            principal_attrs.update(context)
        
        principal = Principal(
            id=principal_id,
            roles=principal_roles,
            attributes=principal_attrs
        )
        
        # Build resource
        resource_attrs = {}
        if resource_id:
            resource_attrs["id"] = resource_id
        if auth_context.tenant_id:
            resource_attrs["tenant_id"] = auth_context.tenant_id
        if auth_context.organization_id:
            resource_attrs["organization_id"] = auth_context.organization_id
        
        resource_obj = Resource(
            kind=resource,
            id=resource_id or "default",
            attributes=resource_attrs
        )
        
        # Check permission
        request = CheckResourcesRequest(
            principal=principal,
            resources=[resource_obj],
            actions=[action]
        )
        
        try:
            response = client.check_resources(request)
            
            # Parse response
            if response.results:
                result = response.results[0]
                allowed = result.actions.get(action, False)
                
                return PermissionResponse(
                    allowed=allowed,
                    reason=None if allowed else "Access denied by policy",
                    metadata={"cerbos_result": result}
                )
            else:
                return PermissionResponse(
                    allowed=False,
                    reason="No policy found for resource",
                    metadata={}
                )
        except Exception as e:
            return PermissionResponse(
                allowed=False,
                reason=f"Cerbos error: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def generate_resource_policy(
        self,
        resource_type: str,
        tenant_id: str,
        rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Cerbos resource policy"""
        policy = {
            "apiVersion": "api.cerbos.dev/v1",
            "resourcePolicy": {
                "version": "default",
                "resource": resource_type,
                "rules": []
            }
        }
        
        for rule in rules:
            cerbos_rule = {
                "actions": rule.get("actions", []),
                "effect": rule.get("effect", "EFFECT_ALLOW"),
                "roles": rule.get("roles", []),
                "condition": rule.get("condition")
            }
            
            # Remove None values
            cerbos_rule = {k: v for k, v in cerbos_rule.items() if v is not None}
            policy["resourcePolicy"]["rules"].append(cerbos_rule)
        
        return policy
    
    def generate_principal_policy(
        self,
        principal_id: str,
        tenant_id: str,
        rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Cerbos principal policy"""
        policy = {
            "apiVersion": "api.cerbos.dev/v1",
            "principalPolicy": {
                "version": "default",
                "principal": principal_id,
                "rules": []
            }
        }
        
        for rule in rules:
            cerbos_rule = {
                "resource": rule.get("resource"),
                "actions": rule.get("actions", []),
                "effect": rule.get("effect", "EFFECT_ALLOW"),
                "condition": rule.get("condition")
            }
            
            # Remove None values
            cerbos_rule = {k: v for k, v in cerbos_rule.items() if v is not None}
            policy["principalPolicy"]["rules"].append(cerbos_rule)
        
        return policy
    
    def build_standard_policies(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Build standard policies for tenant"""
        policies = []
        
        # Superadmin policy - full access
        superadmin_policy = self.generate_resource_policy(
            resource_type="*",
            tenant_id=tenant_id,
            rules=[
                {
                    "actions": ["*"],
                    "effect": "EFFECT_ALLOW",
                    "roles": ["superadmin"],
                    "condition": {
                        "match": {
                            "expr": "P.attr.is_superadmin == true && P.attr.tenant_id == R.attr.tenant_id"
                        }
                    }
                }
            ]
        )
        policies.append(superadmin_policy)
        
        # Admin policy - organization level admin
        admin_policy = self.generate_resource_policy(
            resource_type="*",
            tenant_id=tenant_id,
            rules=[
                {
                    "actions": ["create", "read", "update", "delete", "list", "manage"],
                    "effect": "EFFECT_ALLOW",
                    "roles": ["admin"],
                    "condition": {
                        "match": {
                            "expr": "P.attr.tenant_id == R.attr.tenant_id && P.attr.organization_id == R.attr.organization_id"
                        }
                    }
                }
            ]
        )
        policies.append(admin_policy)
        
        # Member policy - standard user
        member_policy = self.generate_resource_policy(
            resource_type="*",
            tenant_id=tenant_id,
            rules=[
                {
                    "actions": ["read", "list", "create", "update"],
                    "effect": "EFFECT_ALLOW",
                    "roles": ["member"],
                    "condition": {
                        "match": {
                            "expr": "P.attr.tenant_id == R.attr.tenant_id && P.attr.organization_id == R.attr.organization_id"
                        }
                    }
                }
            ]
        )
        policies.append(member_policy)
        
        # Viewer policy - read only
        viewer_policy = self.generate_resource_policy(
            resource_type="*",
            tenant_id=tenant_id,
            rules=[
                {
                    "actions": ["read", "list"],
                    "effect": "EFFECT_ALLOW",
                    "roles": ["viewer"],
                    "condition": {
                        "match": {
                            "expr": "P.attr.tenant_id == R.attr.tenant_id && P.attr.organization_id == R.attr.organization_id"
                        }
                    }
                }
            ]
        )
        policies.append(viewer_policy)
        
        return policies

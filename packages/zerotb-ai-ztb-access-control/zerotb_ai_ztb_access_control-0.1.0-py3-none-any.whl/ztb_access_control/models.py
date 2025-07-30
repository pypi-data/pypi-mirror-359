"""
Pydantic models for ZTB Access Control
"""
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel



class RequestScope(str, Enum):
    """Available request scopes"""
    LIST_TENANTS = "list_tenants"
    LIST_ORGS = "list_orgs"
    UNRESTRICTED = "unrestricted"

class AuthContext(BaseModel):
    """Authentication context extracted from Cognito JWT"""
    user_id: str
    email: str
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None
    request_scope: RequestScope
    roles: List[str] = []
    exp: int
    iat: int
    
    class Config:
        from_attributes = True


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user_id
    request_scope: str
    tenant_id: Optional[str] = None
    org_id: Optional[str] = None
    roles: List[str] = []
    exp: int
    iat: int
    
    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """Permission check response"""
    allowed: bool
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


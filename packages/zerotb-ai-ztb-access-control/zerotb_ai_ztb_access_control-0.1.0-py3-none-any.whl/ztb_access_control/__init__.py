"""
ZTB Access Control - Lightweight authentication and authorization library for Cerbos
"""

from .auth_client import AuthClient
from .config import AuthConfig
from .dependencies import get_current_user, require_permission, require_scope, init_auth_client
from .models import AuthContext, PermissionResponse, RequestScope
from .exceptions import AuthException, PermissionDenied, InvalidToken

__version__ = "0.1.0"
__all__ = [
    "AuthClient",
    "AuthConfig", 
    "get_current_user",
    "require_permission",
    "require_scope",
    "init_auth_client",
    "AuthContext",
    "PermissionResponse",
    "RequestScope",
    "AuthException",
    "PermissionDenied",
    "InvalidToken",
]

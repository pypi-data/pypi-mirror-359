"""
Custom exceptions for ZTB Access Control
"""


class AuthException(Exception):
    """Base authentication exception"""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidToken(AuthException):
    """Raised when JWT token is invalid or expired"""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, 401)


class PermissionDenied(AuthException):
    """Raised when user doesn't have required permission"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, 403)


class InsufficientScope(AuthException):
    """Raised when JWT token doesn't have required scope"""
    def __init__(self, message: str = "Insufficient scope"):
        super().__init__(message, 403)


class TenantNotFound(AuthException):
    """Raised when tenant is not found"""
    def __init__(self, message: str = "Tenant not found"):
        super().__init__(message, 404)


class OrganizationNotFound(AuthException):
    """Raised when organization is not found"""
    def __init__(self, message: str = "Organization not found"):
        super().__init__(message, 404)


class UserNotFound(AuthException):
    """Raised when user is not found"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, 404)


class RoleNotFound(AuthException):
    """Raised when role is not found"""
    def __init__(self, message: str = "Role not found"):
        super().__init__(message, 404)

class ServiceException(AuthException):
    """Raised when there is a service error"""
    def __init__(self, message: str = "Service error"):
        super().__init__(message, 500)

class RuntimeException(AuthException):
    """Raised for runtime exceptions"""
    def __init__(self, message: str = "Runtime error occurred"):
        super().__init__(message, 500)
import os
from pydantic import BaseModel, Field



class AuthConfig(BaseModel):
    """Authentication configuration - focused on Cerbos integration only"""
    
    # Cerbos settings
    cerbos_host: str = Field(default_factory=lambda: os.getenv("CERBOS_HOST", "localhost:3593"))
    cerbos_tls: bool = Field(default_factory=lambda: os.getenv("CERBOS_TLS", "false").lower() == "true")
    
    # # Auth scopes for progressive access
    # list_tenants_scope: str = "list_tenants"
    # list_orgs_scope: str = "list_orgs"
    # unrestricted_scope: str = "unrestricted"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

def get_settings() -> AuthConfig:
    return AuthConfig()

# Create a singleton instance
settings = get_settings()
        

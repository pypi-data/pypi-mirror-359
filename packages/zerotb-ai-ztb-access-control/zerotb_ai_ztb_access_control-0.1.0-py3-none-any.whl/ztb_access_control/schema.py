"""
Database schema creation for ZTB Access Control
"""

# PostgreSQL schema for storing policies and auth data
SCHEMA_SQL = """
-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- Permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    conditions JSONB,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource, action)
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(255) NOT NULL REFERENCES tenants(id),
    role_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, role_name)
);

-- Role permissions mapping
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Cerbos policies storage
CREATE TABLE IF NOT EXISTS cerbos_policies (
    id VARCHAR(255) PRIMARY KEY,
    policy_data JSONB NOT NULL,
    tenant_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_memberships_user_id ON user_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_user_memberships_tenant_org ON user_memberships(tenant_id, org_id);
CREATE INDEX IF NOT EXISTS idx_roles_tenant_id ON roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cerbos_policies_tenant_id ON cerbos_policies(tenant_id);
CREATE INDEX IF NOT EXISTS idx_permissions_resource_action ON permissions(resource, action);

-- Insert default permissions
INSERT INTO permissions (resource, action, description) VALUES
    ('tenant', 'create', 'Create new tenants'),
    ('tenant', 'read', 'Read tenant information'),
    ('tenant', 'update', 'Update tenant information'),
    ('tenant', 'delete', 'Delete tenants'),
    ('tenant', 'list', 'List tenants'),
    ('tenant', 'manage', 'Full tenant management'),
    
    ('organization', 'create', 'Create new organizations'),
    ('organization', 'read', 'Read organization information'),
    ('organization', 'update', 'Update organization information'),
    ('organization', 'delete', 'Delete organizations'),
    ('organization', 'list', 'List organizations'),
    ('organization', 'manage', 'Full organization management'),
    
    ('user', 'create', 'Create new users'),
    ('user', 'read', 'Read user information'),
    ('user', 'update', 'Update user information'),
    ('user', 'delete', 'Delete users'),
    ('user', 'list', 'List users'),
    ('user', 'invite', 'Invite new users'),
    ('user', 'manage', 'Full user management'),
    
    ('role', 'create', 'Create new roles'),
    ('role', 'read', 'Read role information'),
    ('role', 'update', 'Update role information'),
    ('role', 'delete', 'Delete roles'),
    ('role', 'list', 'List roles'),
    ('role', 'assign', 'Assign roles to users'),
    ('role', 'manage', 'Full role management'),
    
    ('framework', 'create', 'Create frameworks'),
    ('framework', 'read', 'Read framework information'),
    ('framework', 'update', 'Update frameworks'),
    ('framework', 'delete', 'Delete frameworks'),
    ('framework', 'list', 'List frameworks'),
    ('framework', 'manage', 'Full framework management'),
    
    ('control', 'create', 'Create controls'),
    ('control', 'read', 'Read control information'),
    ('control', 'update', 'Update controls'),
    ('control', 'delete', 'Delete controls'),
    ('control', 'list', 'List controls'),
    ('control', 'manage', 'Full control management'),
    
    ('test', 'create', 'Create tests'),
    ('test', 'read', 'Read test information'),
    ('test', 'update', 'Update tests'),
    ('test', 'delete', 'Delete tests'),
    ('test', 'list', 'List tests'),
    ('test', 'execute', 'Execute tests'),
    ('test', 'manage', 'Full test management'),
    
    ('evidence', 'create', 'Create evidence'),
    ('evidence', 'read', 'Read evidence information'),
    ('evidence', 'update', 'Update evidence'),
    ('evidence', 'delete', 'Delete evidence'),
    ('evidence', 'list', 'List evidence'),
    ('evidence', 'upload', 'Upload evidence files'),
    ('evidence', 'manage', 'Full evidence management'),
    
    ('task', 'create', 'Create tasks'),
    ('task', 'read', 'Read task information'),
    ('task', 'update', 'Update tasks'),
    ('task', 'delete', 'Delete tasks'),
    ('task', 'list', 'List tasks'),
    ('task', 'assign', 'Assign tasks to users'),
    ('task', 'complete', 'Mark tasks as complete'),
    ('task', 'manage', 'Full task management'),
    
    ('gap_analysis', 'create', 'Create gap analysis'),
    ('gap_analysis', 'read', 'Read gap analysis results'),
    ('gap_analysis', 'update', 'Update gap analysis'),
    ('gap_analysis', 'delete', 'Delete gap analysis'),
    ('gap_analysis', 'list', 'List gap analyses'),
    ('gap_analysis', 'run', 'Run gap analysis'),
    ('gap_analysis', 'manage', 'Full gap analysis management')
ON CONFLICT (resource, action) DO NOTHING;

-- Function to automatically create default roles for new tenants
CREATE OR REPLACE FUNCTION create_default_roles_for_tenant(tenant_id_param VARCHAR(255))
RETURNS VOID AS $$
DECLARE
    superadmin_role_id UUID;
    admin_role_id UUID;
    member_role_id UUID;
    viewer_role_id UUID;
    perm_record RECORD;
BEGIN
    -- Create superadmin role
    INSERT INTO roles (tenant_id, role_name, description, is_system_role)
    VALUES (tenant_id_param, 'superadmin', 'Super administrator with full access', true)
    RETURNING id INTO superadmin_role_id;
    
    -- Create admin role
    INSERT INTO roles (tenant_id, role_name, description, is_system_role)
    VALUES (tenant_id_param, 'admin', 'Administrator with organization-level access', true)
    RETURNING id INTO admin_role_id;
    
    -- Create member role
    INSERT INTO roles (tenant_id, role_name, description, is_system_role)
    VALUES (tenant_id_param, 'member', 'Standard member with basic access', true)
    RETURNING id INTO member_role_id;
    
    -- Create viewer role
    INSERT INTO roles (tenant_id, role_name, description, is_system_role)
    VALUES (tenant_id_param, 'viewer', 'Read-only access', true)
    RETURNING id INTO viewer_role_id;
    
    -- Assign all permissions to superadmin
    FOR perm_record IN SELECT id FROM permissions LOOP
        INSERT INTO role_permissions (role_id, permission_id)
        VALUES (superadmin_role_id, perm_record.id);
    END LOOP;
    
    -- Assign most permissions to admin (excluding tenant management)
    FOR perm_record IN 
        SELECT id FROM permissions 
        WHERE resource != 'tenant' OR action IN ('read', 'list')
    LOOP
        INSERT INTO role_permissions (role_id, permission_id)
        VALUES (admin_role_id, perm_record.id);
    END LOOP;
    
    -- Assign basic permissions to member
    FOR perm_record IN 
        SELECT id FROM permissions 
        WHERE action IN ('read', 'list', 'create', 'update')
        AND resource NOT IN ('tenant', 'user', 'role')
    LOOP
        INSERT INTO role_permissions (role_id, permission_id)
        VALUES (member_role_id, perm_record.id);
    END LOOP;
    
    -- Assign read-only permissions to viewer
    FOR perm_record IN 
        SELECT id FROM permissions 
        WHERE action IN ('read', 'list')
    LOOP
        INSERT INTO role_permissions (role_id, permission_id)
        VALUES (viewer_role_id, perm_record.id);
    END LOOP;
    
END;
$$ LANGUAGE plpgsql;

-- Trigger to create default roles when a tenant is created
CREATE OR REPLACE FUNCTION trigger_create_default_roles()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM create_default_roles_for_tenant(NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER create_tenant_default_roles
    AFTER INSERT ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION trigger_create_default_roles();
"""


async def create_schema(db_url: str):
    """Create database schema"""
    import asyncpg
    
    conn = await asyncpg.connect(db_url)
    try:
        await conn.execute(SCHEMA_SQL)
        print("Database schema created successfully")
    finally:
        await conn.close()


if __name__ == "__main__":
    import asyncio
    import os
    
    db_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    asyncio.run(create_schema(db_url))

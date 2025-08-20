import datetime

from sqlalchemy import Column, UUID, ForeignKey, Table, TIMESTAMP

from applibry_api.infrastructure.persistence.database import Base

role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', UUID, ForeignKey('roles.id', use_alter=True)),
    Column('permission_id', UUID, ForeignKey('permissions.id', use_alter=True)),
    Column('created_at', TIMESTAMP, default=datetime.datetime.utcnow))

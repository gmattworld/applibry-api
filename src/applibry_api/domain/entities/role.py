from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

from applibry_api.domain.entities.role_permission import role_permissions
from applibry_api.domain.entities.root import RootModel


class Role(RootModel):
    __tablename__ = 'roles'
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(150), nullable=False, unique=True)
    description = Column(Text)
    is_system_role = Column(Boolean, default=False)

    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')

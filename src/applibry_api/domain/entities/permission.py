from sqlalchemy import UUID, Column, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from applibry_api.domain.enums.modules import Modules
from applibry_api.domain.entities.role_permission import role_permissions
from applibry_api.domain.entities.root import RootModel


class Permission(RootModel):
    __tablename__ = 'permissions'
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(150), nullable=False, unique=True)
    description = Column(Text)
    module = Column(Enum(Modules), default=Modules.CORE)

    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')

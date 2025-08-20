import datetime
import uuid

from sqlalchemy import Boolean, Column, UUID, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, declared_attr

from applibry_api.infrastructure.persistence.database import Base


class RootModel(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", use_alter=True), nullable=True)

    @declared_attr
    def created_by(cls):
        return relationship("User", foreign_keys=[cls.created_by_id])

    last_updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", use_alter=True), nullable=True)

    @declared_attr
    def last_updated_by(cls):
        return relationship("User", foreign_keys=[cls.last_updated_by_id])

    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id', use_alter=True), nullable=True)

    @declared_attr
    def deleted_by(cls):
        return relationship("User", foreign_keys=[cls.deleted_by_id])

    __abstract__ = True

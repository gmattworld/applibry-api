from sqlalchemy import Column, String, TIMESTAMP, UUID, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from applibry_api.domain.enums.account_type import AccountType
from applibry_api.domain.entities.role import Role
from applibry_api.domain.entities.root import RootModel
from applibry_api.domain.entities.user_app import user_apps
from applibry_api.domain.entities.user_category import user_categories


class User(RootModel):
    __tablename__ = "users"
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    email_confirmed = Column(Boolean, default=False)
    password_hash = Column(String(512), nullable=True)
    public_key = Column(String(100), nullable=True, unique=True)
    verification_code = Column(String(512), nullable=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    invitation_code = Column(String(20), nullable=True)
    is_admin = Column(Boolean, default=False)
    receive_newsletter = Column(Boolean, default=False)
    phone_number = Column(String(20), nullable=True)
    profession = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    phone_number_confirmed = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    lockout_end = Column(TIMESTAMP, nullable=True)
    lockout_enabled = Column(Boolean, default=False)
    access_failed_count = Column(Integer, default=0)
    role_id = Column(UUID, ForeignKey("roles.id", use_alter=True), nullable=True)
    role = relationship(Role, foreign_keys=[role_id])
    password_reset_code = Column(String(512), nullable=True)
    password_reset_requested = Column(Boolean, default=False)

    account_type = Column(Enum(AccountType), default=AccountType.STARTER)
    last_subscription_date = Column(TIMESTAMP, nullable=True)
    next_subscription_date = Column(TIMESTAMP, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_verified_at = Column(TIMESTAMP, nullable=True)
    is_preference_configured = Column(Boolean, default=False)

    apps = relationship('App', secondary=user_apps, back_populates='users')
    categories = relationship('Category', secondary=user_categories, back_populates='users')

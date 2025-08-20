from sqlalchemy import Column, String, Text, UUID, ForeignKey, Float, Integer, Boolean, TIMESTAMP, Enum
from sqlalchemy.orm import relationship

from applibry_api.domain.enums.app_status import AppStatus
from applibry_api.domain.enums.pricing_model import PricingModel
from applibry_api.domain.entities.app_platform import app_platforms
from applibry_api.domain.entities.app_tag import app_tags
from applibry_api.domain.entities.category import Category
from applibry_api.domain.entities.root import RootModel
from applibry_api.domain.entities.user_app import user_apps


class App(RootModel):
    __tablename__ = 'apps'
    name = Column(String(255), nullable=False, unique=True)  # Tool name
    slug = Column(String(500), nullable=False, unique=True)  # Tool name
    description = Column(Text, nullable=True)  # Brief description of the tool
    brief = Column(Text, nullable=False)
    trending = Column(Boolean, nullable=False, default=False)
    website = Column(String(255), nullable=True)  # Link to the tool's website
    icon = Column(Text, nullable=True)
    banner = Column(Text, nullable=True)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(String(255), nullable=True)
    status = Column(Enum(AppStatus), default=AppStatus.DRAFT)

    published_at = Column(TIMESTAMP)

    # Pricing Info
    pricing_model = Column(Enum(PricingModel), default=PricingModel.FREE, nullable=False)  # E.g., Free, Freemium, Paid, Enterprise
    price = Column(Float, nullable=True)  # Base price if applicable

    # Tool Details
    api_available = Column(Boolean, default=False)  # Whether the tool offers an API
    integration_guide = Column(Text)  # Link or text for integration guide
    documentation_link = Column(String(255))  # Link to official documentation

    # User Engagement
    ratings = Column(Float, default=0.0)  # Average user rating
    reviews = Column(Integer, default=0)  # Number of reviews
    subscribers = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    rank = Column(Integer, default=0)

    # Relationships
    category_id = Column(UUID, ForeignKey("categories.id", use_alter=True), nullable=False)
    category = relationship(Category, foreign_keys=[category_id])

    # reviews = relationship("Review", back_populates="apps", cascade="all, delete-orphan")
    tags = relationship('Tag', secondary=app_tags, back_populates='apps')
    platforms = relationship('Platform', secondary=app_platforms, back_populates='apps')
    users = relationship('User', secondary=user_apps, back_populates='apps')

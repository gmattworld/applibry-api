from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, UUID
from sqlalchemy.orm import relationship

from applibry_api.domain.entities.app import App
from applibry_api.domain.entities.root import RootModel
from applibry_api.domain.entities.user import User


class Review(RootModel):
    __tablename__ = 'reviews'
    comment = Column(String(100), nullable=False, unique=True)
    upvotes = Column(Integer, default=0)


    # Relationships
    app_id = Column(UUID, ForeignKey("apps.id", use_alter=True), nullable=False)
    app = relationship(App, foreign_keys=[app_id])

    user_id = Column(UUID, ForeignKey("users.id", use_alter=True), nullable=False)
    user = relationship(User, foreign_keys=[user_id])
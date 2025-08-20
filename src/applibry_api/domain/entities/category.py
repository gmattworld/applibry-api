from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship

from applibry_api.domain.entities.root import RootModel
from applibry_api.domain.entities.user_category import user_categories


class Category(RootModel):
    __tablename__ = 'categories'
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(200), nullable=True)
    app_count = Column(Integer, default=0)
    subscribers = Column(Integer, default=0)

    users = relationship('User', secondary=user_categories, back_populates='categories')

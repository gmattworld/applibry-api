from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from applibry_api.domain.entities.app_platform import app_platforms
from applibry_api.domain.entities.root import RootModel


class Platform(RootModel):
    __tablename__ = 'platforms'
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    apps = relationship('App', secondary=app_platforms, back_populates='platforms')

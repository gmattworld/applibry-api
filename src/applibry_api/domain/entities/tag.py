from sqlalchemy import Column, String, Text, UUID, ForeignKey
from sqlalchemy.orm import relationship

from applibry_api.domain.entities.app_tag import app_tags
from applibry_api.domain.entities.root import RootModel


class Tag(RootModel):
    __tablename__ = 'tags'
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    apps = relationship('App', secondary=app_tags, back_populates='tags')

import datetime

from sqlalchemy import Column, UUID, ForeignKey, Table, TIMESTAMP

from applibry_api.infrastructure.persistence.database import Base

app_tags = Table('app_tags', Base.metadata,
        Column('app_id', UUID, ForeignKey('apps.id', use_alter=True)),
        Column('tag_id', UUID, ForeignKey('tags.id', use_alter=True)),
        Column('created_at', TIMESTAMP, default=datetime.datetime.utcnow))

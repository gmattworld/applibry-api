import datetime

from sqlalchemy import Column, UUID, ForeignKey, Table, TIMESTAMP

from applibry_api.infrastructure.persistence.database import Base

app_platforms = Table('app_platforms', Base.metadata,
        Column('app_id', UUID, ForeignKey('apps.id', use_alter=True)),
        Column('platform_id', UUID, ForeignKey('platforms.id', use_alter=True)),
        Column('created_at', TIMESTAMP, default=datetime.datetime.utcnow))

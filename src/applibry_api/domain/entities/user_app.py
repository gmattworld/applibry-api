import datetime

from sqlalchemy import Column, UUID, ForeignKey, Table, DateTime, TIMESTAMP

from applibry_api.infrastructure.persistence.database import Base

user_apps = Table('user_apps', Base.metadata,
      Column('user_id', UUID, ForeignKey('users.id', use_alter=True)),
      Column('app_id', UUID, ForeignKey('apps.id', use_alter=True)),
      Column('created_at', TIMESTAMP, default=datetime.datetime.utcnow))

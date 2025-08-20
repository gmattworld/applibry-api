from sqlalchemy import Column, UUID, ForeignKey, Index, PrimaryKeyConstraint, Table, TIMESTAMP, func

from applibry_api.infrastructure.persistence.database import Base

# user_categories = Table('user_categories', Base.metadata,
#     Column('user_id', UUID, ForeignKey('users.id', use_alter=True)),
#     Column('category_id', UUID, ForeignKey('categories.id', use_alter=True)),
#     Column('created_at', TIMESTAMP, default=datetime.datetime.utcnow))

user_categories = Table(
    "user_categories", Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), server_default=func.now(), nullable=False),
    PrimaryKeyConstraint("user_id", "category_id", name="pk_user_categories"),
)

# Optional single-column indexes (composite PK already indexes both together)
Index("ix_user_categories_user_id", user_categories.c.user_id)
Index("ix_user_categories_category_id", user_categories.c.category_id)

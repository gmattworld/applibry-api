from enum import Enum


class AppStatus(Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    PENDING_REVIEW = "Pending Review"
from enum import Enum


class PricingModel(Enum):
    FREE = "Free"
    FREEMIUM = "Freemium"
    PAID = "Paid"
    ENTERPRISE = "Enterprise"
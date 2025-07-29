from sqlalchemy import Column, String, Integer

from abs_repository_core.models import BaseModel


class Subscription(BaseModel):
    __tablename__ = "gov_subscriptions"
    
    resource_type = Column(String(255), nullable=False)
    site_id = Column(String(255), nullable=False)
    resource_id = Column(String(255), nullable=False)
    change_type = Column(String(255), nullable=False)
    provider_name = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    
    # user = relationship(Users, backref="subscriptions")

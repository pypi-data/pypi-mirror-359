from pydantic import BaseModel, Field
from typing import Optional


class Subscription(BaseModel):
    resource_type: str
    site_id: str
    resource_id: str
    change_type: str
    provider_name: str

    user_id: int

    class Config:
        extra = "allow"


class SubscribeRequestSchema(BaseModel):
    resource_type: Optional[str] = Field(None, description="Type of resource: 'list' or 'drive'")
    site_id: Optional[str] = Field(None, description="SharePoint site ID")
    resource_id: Optional[str] = Field(None, description="List or Drive ID")
    change_type: str = Field("updated", description="Change types to subscribe to")
    expiration_days: int = Field(15, description="Subscription expiration in days (max 30)")
    automation_id: str = Field(..., description="Automation ID")

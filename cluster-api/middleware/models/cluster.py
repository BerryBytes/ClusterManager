import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Cluster(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str = Field(...)
    userId: str = Field(alias="user_id")
    status: str = Field(...)
    kube_version: str = Field(alias="kube_version")
    hostClusterId: str = Field(alias="host_cluster_id")
    subscriptionId: str = Field(alias="subscription_id")
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "one",
                "user_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "host_cluster_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "subscription_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
            }
        }

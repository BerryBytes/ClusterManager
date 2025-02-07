from pydantic import BaseModel,Field
from typing import Optional



class ClusterRequest(BaseModel):
    name: str 
    subscriptionId: str = Field(alias="subscription_id")
    region: str = Field(alias="region")
    kube_version: Optional[str] = Field(alias="kube_version",default="v1.30.0")

    class Config:
        schema_extra = {
            "example":{
                "name":"cluster-name",
                "subscription_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "region":"us-east-1",
                "kube_version":"v1.27.0"
            }
        }

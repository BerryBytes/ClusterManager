from pydantic import BaseModel,Field
from typing import Optional



class ClusterUpgradeRequest(BaseModel):
    kube_version: str = Field(alias="kube_version")

    class Config:
        schema_extra = {
            "example":{
                "kube_version":"v1.27.0"
            }
        }

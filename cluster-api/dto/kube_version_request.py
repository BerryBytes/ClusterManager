from pydantic import BaseModel, Field
from datetime import datetime

class KubeVersionRequest(BaseModel):
    name: str
    kube_version: str
    active: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "example_name",
                "kube_version": "1.30.1",
                "active": True
            }
        }

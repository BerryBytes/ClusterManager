import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class KubeVersion(BaseModel):
    name: str
    kube_version: str
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    active: bool

    class Config:
        orm_mode = True

import uuid
from datetime import datetime
from pydantic import BaseModel, Field



class HostCluster(BaseModel):
    id: str = Field(default_factory=uuid.uuid4,alias="_id")
    name: str = Field(...)
    region: str = Field(...)
    provider: str = Field(...)
    nodes: int = Field(...)
    active: bool = Field(...)
    version: str = Field(...)
    userId: str = Field(alias="user_id")
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example":{
                "name": "cluster 1",
                "region": "us-east-1",
                "provider": "aws",
                "nodes": 1,
                "active": False,
                "version": "1.25"
            }
        }
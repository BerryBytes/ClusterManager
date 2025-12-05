"""DTOs for cluster API: host cluster request models."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class HostClusterRequest(BaseModel):
    """Request model for creating or updating a host cluster."""

    name: str = Field(...)
    region: str = Field(...)
    provider: str = Field(...)
    nodes: int = Field(...)
    active: bool = Field(...)
    version: str = Field(...)

    class Config:
        """Pydantic configuration for host_cluster_request,including schema example."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "cluster 1",
                "region": "us-east-1",
                "provider": "aws",
                "nodes": 1,
                "active": False,
                "version": "1.25",
            }
        }

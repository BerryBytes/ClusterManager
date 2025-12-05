"""DTOs for cluster API: kube version request models."""
from datetime import datetime

from pydantic import BaseModel, Field


class KubeVersionRequest(BaseModel):
    """Request model for specifying a Kubernetes version for a cluster."""

    name: str
    kube_version: str
    active: bool = Field(default=True)

    class Config:
        """Pydantic configuration for KubeVersionRequest,including schema example."""

        json_schema_extra = {
            "example": {
                "name": "example_name",
                "kube_version": "1.30.1",
                "active": True,
            }
        }

"""DTOs for cluster API: cluster upgrade request models."""
from typing import Optional

from pydantic import BaseModel, Field


class ClusterUpgradeRequest(BaseModel):
    """Request model for upgrading a Kubernetes cluster."""

    kube_version: str = Field(alias="kube_version")

    class Config:
        """
        Pydantic configuration for cluster_upgrade_request,
        including schema example.
        """

        schema_extra = {"example": {"kube_version": "v1.27.0"}}

"""Model representing a Kubernetes version."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class KubeVersion(BaseModel):
    """Represents a Kubernetes version entry."""

    name: str
    kube_version: str
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    active: bool

    class Config:
        """Pydantic configuration for ORM compatibility."""

        orm_mode = True

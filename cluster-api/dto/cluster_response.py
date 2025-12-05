"""DTOs for cluster API: response models."""
from models.host_cluster import HostCluster
from models.subscription import Subscription
from models.user import User
from pydantic import BaseModel


class ClusterResponse(BaseModel):
    """Response model representing a Kubernetes cluster."""

    id: str
    name: str
    status: str
    created: str
    kube_version: str
    user: User
    subscription: Subscription
    hostCluster: HostCluster

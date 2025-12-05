"""DTOs for cluster API: cluster status request models."""
from pydantic import BaseModel


class ClusterStatusRequest(BaseModel):
    """Request model for updating or querying the status of a Kubernetes cluster."""

    name: str
    id: str
    status: str

    class Config:
        """Pydantic configuration for ClusterStatusRequest,including schema example."""

        schema_extra = {
            "example": {
                "name": "cluster-name",
                "id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "status": "Running",
            }
        }

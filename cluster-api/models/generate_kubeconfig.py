"""Model for generating a kubeconfig with expiry time."""
from pydantic import BaseModel


class GenerateKubeconfig(BaseModel):
    """Request model for generating a temporary kubeconfig."""

    expiryTime: str
    clusterId: str

    class Config:
        """Pydantic configuration for field population and schema examples."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "expiryTime": "1h20m",
                "clusterId": "066de609-b04a-4b30-b46c-32537c7f1f6e",
            }
        }

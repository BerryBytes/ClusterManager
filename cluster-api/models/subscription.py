"""Model representing a subscription plan and its resource limits."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Subscription(BaseModel):
    """Represents a subscription with resource quotas and utility methods."""

    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    pods: int = Field(...)
    service: int = Field(...)
    configMap: int = Field(alias="config_map")
    persistanceVolClaims: int = Field(alias="persistance_vol_claims")
    replicationCtl: int = Field(alias="replication_ctl")
    secrets: int = Field(alias="secrets")
    loadbalancer: int = Field(...)
    nodePort: int = Field(alias="node_port")
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    def is_subscription_upgrade(self, new_plan):
        """Determine if the new plan exceeds current resource allocations."""
        if new_plan.pods > self.pods:
            return True
        if new_plan.service > self.service:
            return True
        if new_plan.configMap > self.configMap:
            return True
        if new_plan.persistanceVolClaims > self.persistanceVolClaims:
            return True
        if new_plan.replicationCtl > self.replicationCtl:
            return True
        if new_plan.secrets > self.secrets:
            return True
        if new_plan.loadbalancer > self.loadbalancer:
            return True
        if new_plan.nodePort > self.nodePort:
            return True
        return False

    class Config:
        """Pydantic configuration for field population and schema examples."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "basic",
                "pods": 5,
                "service": 5,
                "config_map": 5,
                "persistance_vol_claims": 5,
                "replication_ctl": 5,
                "secrets": 5,
                "loadbalancer": 5,
                "node_port": 5,
            }
        }

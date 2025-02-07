from pydantic import BaseModel
from models.host_cluster import HostCluster
from models.subscription import Subscription

from models.user import User


class ClusterResponse(BaseModel):
    id:str
    name: str
    status:str
    created: str
    kube_version: str
    user: User
    subscription: Subscription
    hostCluster: HostCluster
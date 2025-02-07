from pyparsing import Any
from models.subscription import Subscription


def subscription_from_dict(res: Any):
    return Subscription(
        name=res['name'],
        pods=res['pods'],
        service=res['service'],
        config_map=res['config_map'],
        persistance_vol_claims=res['persistance_vol_claims'],
        replication_ctl=res['replication_ctl'],
        secrets=res['secrets'],
        loadbalancer=res['loadbalancer'],
        node_port=res['node_port']
    )

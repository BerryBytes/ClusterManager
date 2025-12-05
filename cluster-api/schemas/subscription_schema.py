"""
Module for creating Subscription objects from dictionaries.

Contains utility functions for converting data to Subscription model instances.
"""
from models.subscription import Subscription
from pyparsing import Any


def subscription_from_dict(res: Any):
    """Convert a dictionary to a Subscription object."""
    return Subscription(
        name=res["name"],
        pods=res["pods"],
        service=res["service"],
        config_map=res["config_map"],
        persistance_vol_claims=res["persistance_vol_claims"],
        replication_ctl=res["replication_ctl"],
        secrets=res["secrets"],
        loadbalancer=res["loadbalancer"],
        node_port=res["node_port"],
    )

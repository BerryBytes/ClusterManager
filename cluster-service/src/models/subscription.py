"""Module for subscription-related data structures and parsing utilities."""


class Subscription:
    """Represents a Kubernetes subscription configuration."""

    def __init__(
        self,
        name,
        pods,
        service,
        config_map,
        persistence_vol_claims,
        replication_ctl,
        secrets,
        loadbalancer,
        node_port,
    ):
        """Initialize a Subscription instance.

        Args:
            name (str): Name of the subscription.
            pods (Any): Pod specifications.
            service (Any): Service specifications.
            config_map (Any): ConfigMap specifications.
            persistence_vol_claims (Any): Persistent volume claims.
            replication_ctl (Any): Replication controller configuration.
            secrets (Any): Secrets associated with the subscription.
            loadbalancer (Any): Load balancer configuration.
            node_port (Any): Node port configuration.
        """
        self.name = name
        self.pods = pods
        self.service = service
        self.config_map = config_map
        self.persistence_vol_claims = persistence_vol_claims
        self.replication_ctl = replication_ctl
        self.secrets = secrets
        self.loadbalancer = loadbalancer
        self.node_port = node_port


def parse_subscription_json(json_data):
    """Parse a JSON dictionary and return a Subscription instance.

    Args:
        json_data (dict): JSON data representing a subscription.

    Returns:
        Subscription: Populated Subscription object.
    """
    return Subscription(
        name=json_data["name"],
        pods=json_data["pods"],
        service=json_data["service"],
        config_map=json_data["config_map"],
        persistence_vol_claims=json_data["persistance_vol_claims"],
        replication_ctl=json_data["replication_ctl"],
        secrets=json_data["secrets"],
        loadbalancer=json_data["loadbalancer"],
        node_port=json_data["node_port"],
    )

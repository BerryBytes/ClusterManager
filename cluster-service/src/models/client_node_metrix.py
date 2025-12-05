"""Module for storing and managing client node metrics."""


class ClientNodesMetrics:
    """Stores metrics for client nodes."""

    def __init__(self):
        """Initialize an empty dictionary to store metrics by node name."""
        self.metrics = {}  # Dictionary to store metrics by node name

    def add_metric(self, node_name, metric):
        """Add or update a metric for a specific node.

        Args:
            node_name (str): The name of the node.
            metric (Any): The metric data associated with the node.
        """
        self.metrics[node_name] = metric

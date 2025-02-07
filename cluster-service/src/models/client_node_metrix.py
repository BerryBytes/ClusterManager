class ClientNodesMetrics:
    def __init__(self):
        self.metrics = {}  # Dictionary to store metrics by node name

    def add_metric(self, node_name, metric):
        self.metrics[node_name] = metric
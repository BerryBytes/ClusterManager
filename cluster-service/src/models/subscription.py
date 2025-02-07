class Subscription:
    def __init__(self, name, pods, service, config_map, persistence_vol_claims, replication_ctl, secrets, loadbalancer, node_port):
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
    return Subscription(
        name=json_data['name'],
        pods=json_data['pods'],
        service=json_data['service'],
        config_map=json_data['config_map'],
        persistence_vol_claims=json_data['persistance_vol_claims'],
        replication_ctl=json_data['replication_ctl'],
        secrets=json_data['secrets'],
        loadbalancer=json_data['loadbalancer'],
        node_port=json_data['node_port']
    )


"""Utility functions for managing Kubernetes clusters and vclusters."""
import time

from kubernetes import client
from src.models.subscription import Subscription


def generate_vclusterYaml(name, namespace, host, kube_version):
    """Generate the YAML configuration for a vcluster."""
    yaml_template = """
apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
kind: VCluster
metadata:
  name: {name}
  namespace: {namespace}
spec:
  controlPlaneEndpoint:
    host: {host}
    port: 443
  helmRelease:
    chart:
      name: vcluster
      repo: https://charts.loft.sh
      version: 0.20.0
    values: |
      controlPlane:
        distro:
          k8s:
            enabled: false
            version: ''
            apiServer:
              enabled: true
              image:
                registry: registry.k8s.io
                repository: kube-apiserver
                tag: {kube_version}
            controllerManager:
              enabled: true
              image:
                registry: registry.k8s.io
                repository: kube-controller-manager
                tag: {kube_version}
        proxy:
          extraSANs:
          - {host}
"""
    return yaml_template.format(
        name=name, namespace=namespace, host=host, kube_version=kube_version
    )


def generate_cluster_yaml(name: str, namespace: str):
    """Generate the YAML configuration for a Cluster."""
    yaml_template = """
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: {name}
  namespace: {namespace}
spec:
  controlPlaneRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
    kind: VCluster
    name: {name}
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1alpha1
    kind: VCluster
    name: {name}
"""
    return yaml_template.format(
        name=name,
        namespace=namespace,
    )


def generate_resource_quota_yaml(subscription: Subscription, namespace: str):
    """Generate the YAML configuration for a ResourceQuota based on subscription."""
    yaml_template = """
apiVersion: v1
kind: ResourceQuota
metadata:
  name: {name}
  namespace: {namespace}
spec:
  hard:
    pods: {pod}
    services: {service}
    configmaps: {config_map}
    persistentvolumeclaims: {persistent_volume_claims}
    replicationcontrollers: {replication_controllers}
    secrets: {secrets}
    services.loadbalancers: {load_balancers}
    services.nodeports: {node_ports}
"""
    return yaml_template.format(
        name=subscription.name,
        namespace=namespace,
        pod=subscription.pods,
        service=subscription.service,
        config_map=subscription.config_map,
        persistent_volume_claims=subscription.persistence_vol_claims,
        replication_controllers=subscription.replication_ctl,
        secrets=subscription.secrets,
        load_balancers=subscription.loadbalancer,
        node_ports=subscription.node_port,
    )


def createNamespace(namespace_name):
    """Create a Kubernetes namespace. Deletes it first if it already exists."""
    api_client = client.CoreV1Api()
    try:
        # Check if the namespace already exists
        try:
            api_client.read_namespace(name=namespace_name)
            print(f"Namespace '{namespace_name}' already exists. Deleting it...")
            api_client.delete_namespace(
                name=namespace_name, body=client.V1DeleteOptions()
            )
            print(f"Namespace '{namespace_name}' deleted successfully.")

            # Wait for the namespace to be fully deleted
            wait_for_namespace_deletion(namespace_name)

        except client.rest.ApiException as e:
            if e.status == 404:
                print(
                    f"Namespace '{namespace_name}' does not exist. Proceeding to create it."
                )
            else:
                raise e
        api_client.create_namespace(
            client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace_name))
        )
        print(f"Namespace '{namespace_name}' created successfully")
    except client.rest.ApiException as e:
        print(f"Error handling namespace '{namespace_name}': {str(e)}")
        raise e


def wait_for_namespace_deletion(namespace_name):
    """Wait until the namespace is fully deleted."""
    api_client = client.CoreV1Api()

    while True:
        try:
            # Attempt to read the namespace to see if it still exists
            api_client.read_namespace(name=namespace_name)
            print(f"Namespace '{namespace_name}' is still being deleted. Waiting...")
            time.sleep(5)

        except client.rest.ApiException as e:
            if e.status == 404:
                print(f"Namespace '{namespace_name}' has been deleted successfully.")
                break
            else:
                print(f"Error checking namespace '{namespace_name}': {str(e)}")
                raise e


def add_labels_to_statefulset(namespace, sts_name, labels):
    """Add labels to an existing Kubernetes StatefulSet."""
    try:
        apps_v1 = client.AppsV1Api()

        statefulset = apps_v1.read_namespaced_stateful_set(sts_name, namespace)

        # Add labels to the StatefulSet's template metadata labels
        statefulset.spec.template.metadata.labels.update(labels)
        # statefulset.spec.template.metadata.annotations = annotations

        updated_statefulset = apps_v1.patch_namespaced_stateful_set(
            sts_name, namespace, statefulset
        )

        return updated_statefulset
    except Exception as e:
        return f"An error occurred: {e}"

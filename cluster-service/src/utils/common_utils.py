"""
Utility functions for Kubernetes resource checks.

Includes kubeconfig parsing and calculating cluster resource usage.
"""

import base64
import logging
import tempfile

from kubernetes import client, config
from src.utils.best_cluster_utils import get_best_cluster


def get_available_resources_fromSecret(kubeconfigSecrets):
    """
    Extract CPU and memory usage percentages from kubeconfig secrets.

    Decodes kubeconfigs, collects node metrics, and returns the best cluster
    based on resource availability.
    """
    try:
        clusterResource = {}
        for Kube_secret in kubeconfigSecrets:
            # Decode the base64-encoded kubeconfig
            decoded_kubeconfig = base64.b64decode(Kube_secret["encoded_config"])

            # Write the decoded kubeconfig to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(decoded_kubeconfig)
                temp_file.flush()

                # Load the kubeconfig and create the client
                config.load_kube_config(temp_file.name)
            # Clean up the temporary file
            temp_file.close()
            api = client.CustomObjectsApi()
            api_client = client.CoreV1Api()
            k8s_nodes_matrix = api.list_cluster_custom_object(
                "metrics.k8s.io", "v1beta1", "nodes"
            )
            nodes = api_client.list_node().items

            # Use a dictionary to store metrics
            client_nodes_metrics = {}

            # Correctly call cluster_load to get percentages
            percentage = cluster_load(nodes, k8s_nodes_matrix, client_nodes_metrics)

            clusterResource[Kube_secret["id"]] = {}
            clusterResource[Kube_secret["id"]]["CPU"] = percentage["PercCPU"]
            clusterResource[Kube_secret["id"]]["MEMORY"] = percentage["PercMEM"]

        best = get_best_cluster(clusterResource)
        print("Best Cluster :: ", best)
        return best
    except Exception as e:
        logging.error("error occurs :: %s", str(e))  # Fixed string formatting
        return {
            "error": f"Error occurred: {str(e)}"
        }  # Return a dictionary for consistent response


def cluster_load(nos, nmx, mx):
    """
    Calculate used and total CPU/memory to produce utilization percentages.

    Returns a dictionary containing PercCPU and PercMEM values.
    """
    if nos is None or nmx is None:
        raise ValueError("Invalid node or node metrics lists")

    node_metrics = {}
    for no in nos:
        node_name = no.metadata.name
        node_metrics[node_name] = {
            "AllocatableCPU": ToMilliValue(no.status.allocatable["cpu"]),
            "AllocatableMEM": ToMB(no.status.allocatable["memory"]),
            "CurrentCPU": 0,  # Default to 0 for new nodes without metrics
            "CurrentMEM": 0,  # Default to 0 for new nodes without metrics
        }

    for mx_item in nmx["items"]:
        node_name = mx_item["metadata"]["name"]
        if node_name in node_metrics:
            node = node_metrics[node_name]
            node["CurrentCPU"] = ToMilliValue(mx_item["usage"]["cpu"])
            node["CurrentMEM"] = ToMB(mx_item["usage"]["memory"])
            node_metrics[node_name] = node

    ccpu, cmem, tcpu, tmem = 0, 0, 0, 0
    for metrics in node_metrics.values():
        ccpu += metrics["CurrentCPU"]
        cmem += metrics["CurrentMEM"]
        tcpu += metrics["AllocatableCPU"]
        tmem += metrics["AllocatableMEM"]

    mx["PercCPU"] = to_percentage(ccpu, tcpu)
    mx["PercMEM"] = to_percentage(cmem, tmem)

    return mx


def to_percentage(value, total):
    """
    Return percentage value of 'value' relative to 'total'.

    Avoids division-by-zero by returning 0.0 when total is zero.
    """
    if total == 0:
        return 0.0
    return (value / total) * 100.0


# Helper function to convert to MB
def ToMB(value):
    """
    Convert memory values (Ki/Mi/Gi/Ti) into MB.

    Returns numeric MB value.
    """
    if isinstance(value, str):
        if value.endswith("Ki"):
            value = int(value[:-2]) / 1024
        elif value.endswith("Mi"):
            value = int(value[:-2])
        elif value.endswith("Gi"):
            value = int(value[:-2]) * 1024
        elif value.endswith("Ti"):
            value = int(value[:-2]) * 1024 * 1024
        else:
            value = int(value) / (1024 * 1024)
    return value


def ToMilliValue(value):
    """
    Convert CPU units (n, u, m, cores) into millicores.

    Returns integer millicore value.
    """
    if isinstance(value, str):
        if value.endswith("n"):
            return int(value[:-1]) / 1000000
        elif value.endswith("u"):
            return int(value[:-1]) / 1000
        elif value.endswith("m"):
            return int(value[:-1])
        else:
            try:
                return int(value) * 1000
            except ValueError:
                raise ValueError("Unknown CPU value format: " + value)
    else:
        return int(value)


def check_namespace_existence(namespace):
    """Return True if a namespace exists, otherwise False."""
    try:
        v1 = client.CoreV1Api()
        v1.read_namespace(name=namespace)
        return True  # Namespace exists
    except Exception as e:
        return False


def get_pod_status(namespace: str, name: str):
    """
    Return the current status (phase) of a pod.

    If the namespace does not exist, returns 'Failed'. On any other
    error, returns 'Creating'.
    """
    try:
        if not check_namespace_existence(namespace):
            return "Failed"
        v1 = client.CoreV1Api()
        pod_name = name + "-0"
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        pod_status = pod.status.phase
        return pod_status
    except Exception as e:
        logging.error("error occurs while fetching status :: %s", str(e))
        return "Creating"

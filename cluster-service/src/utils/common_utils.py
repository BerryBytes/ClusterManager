import base64
import logging
import tempfile
from kubernetes import client, config

from src.models.client_node_metrix import ClientNodesMetrics
from src.utils.best_cluster_utils import get_best_cluster


def get_available_resources_fromSecret(kubeconfigSecrets):
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
            k8s_nodes_matrix = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
            nodes = api_client.list_node().items 
            client_nodes_metrics = ClientNodesMetrics()
            percentage = cluster_load(nodes,k8s_nodes_matrix,client_nodes_metrics)

            clusterResource[Kube_secret["id"]] = {}
            clusterResource[Kube_secret["id"]]["CPU"] =percentage["PercCPU"]
            clusterResource[Kube_secret["id"]]["MEMORY"] =percentage["PercMEM"]

        best = get_best_cluster(clusterResource)
        print("Best Cluster :: ",best)     
        return best
    except Exception as e:
        logging.error("error occours :: ",str(e))
        return f"Error occurred: {str(e)}"



def cluster_load(nos, nmx, mx):
    if nos is None or nmx is None:
        raise ValueError("Invalid node or node metrics lists")

    node_metrics = {}
    for no in nos:
        node_metrics[no.metadata.name] = {
            "AllocatableCPU":ToMilliValue(no.status.allocatable["cpu"]),
            "AllocatableMEM":ToMB(no.status.allocatable["memory"])
        }

    for mx in nmx['items']:
        if mx['metadata']['name'] in node_metrics:
            node = node_metrics[mx['metadata']['name']]
            node["CurrentCPU"] = ToMilliValue(mx['usage']['cpu'])
            node["CurrentMEM"] = ToMB(mx['usage']['memory'])
            node_metrics[mx['metadata']['name']] = node

    ccpu, cmem, tcpu, tmem = 0, 0, 0, 0
    for mx in node_metrics.values():
        ccpu += mx["CurrentCPU"]
        cmem += mx["CurrentMEM"]
        tcpu += mx["AllocatableCPU"]
        tmem += ToMB(mx["AllocatableMEM"])
    

    mx["PercCPU"] = to_percentage(ccpu, tcpu)
    mx["PercMEM"] = to_percentage(cmem, tmem)

    return mx


def to_percentage(value, total):
    if total == 0:
        return 0.0
    return (value / total) * 100.0 


# Helper function to convert to MB
def ToMB(value):
    if isinstance(value, str):
        if value.endswith('Ki'):
            value = int(value[:-2]) / 1024
        elif value.endswith('Mi'):
            value = int(value[:-2])
        elif value.endswith('Gi'):
            value = int(value[:-2]) * 1024
        elif value.endswith('Ti'):
            value = int(value[:-2]) * 1024 * 1024
        else:
            value = int(value) / (1024 * 1024)
    return value 
    
def ToMilliValue(value):
    if isinstance(value, str):
        if value.endswith('n'):
            return int(value[:-1]) / 1000000  
        elif value.endswith('u'):
            return int(value[:-1]) / 1000
        elif value.endswith('m'):
            return int(value[:-1])
        else:
            try:
                return int(value) * 1000
            except ValueError:
                raise ValueError("Unknown CPU value format: " + value)
    else:
        return int(value)
    
def check_namespace_existence(namespace):
    try:
        v1 = client.CoreV1Api()
        v1.read_namespace(name=namespace)
        return True  # Namespace exists
    except Exception as e:
        return False    
    

def get_pod_status(namespace:str, name:str):
    try:
        if not check_namespace_existence(namespace):
            return "Failed"
        v1 = client.CoreV1Api()
        pod_name = name + "-0"
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        pod_status = pod.status.phase
        return pod_status
    except Exception as e:
        logging.error("error occurs while fetching status :: %s",str(e))
        return "Creating"   
        
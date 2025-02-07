import base64
import logging
import os
import tempfile
import time
import json
from flask import jsonify, request
import yaml
from kubernetes import client, config
from http.client import HTTPException
from src.utils.common_utils import get_available_resources_fromSecret, get_pod_status
from src.utils.secret_utils import get_vault_secret
from src.utils.cluster_utils import add_labels_to_statefulset, createNamespace, generate_vclusterYaml
from src.utils.cluster_utils import generate_cluster_yaml, generate_resource_quota_yaml
from src.models.subscription import parse_subscription_json

def load_kubernetes_client(base64_kubeconfig):
    decoded_kubeconfig = base64.b64decode(base64_kubeconfig)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(decoded_kubeconfig)
        temp_file.flush()
        config.load_kube_config(temp_file.name)
        k8s_client = client
    temp_file.close()
    return k8s_client

def create_cluster_usecase(data):
    logging.info("Published data Create Cluster :: " + json.dumps(data["data"]))
    secret = get_vault_secret(data["data"]["host_cluster_id"])
    host_cluster_name = data["data"]["host_cluster_name"]
    kube_version = data["data"]["cluster"]["kube_version"]
    load_kubernetes_client(secret)

    namespace = data["data"]["cluster"]["name"] + "-vcluster"
    name = data["data"]["cluster"]["name"]
    cluster_id = data["data"]["cluster"]["id"]
    domain = os.getenv('HOST_NAME')
    host = f'{name}.{host_cluster_name}.{domain}'

    vcluster = generate_vclusterYaml(namespace=namespace, name=name, host=host, kube_version=kube_version)
    custom_resource = generate_cluster_yaml(namespace=namespace, name=name)
    logging.info("Subscription data: " + json.dumps(data["data"]["subscription"]))

    subscriptionData = parse_subscription_json(data["data"]["subscription"])
    quota = generate_resource_quota_yaml(subscription=subscriptionData, namespace=namespace)

    try:
        try:
            existing_resource = client.CustomObjectsApi().get_namespaced_custom_object(
                group="infrastructure.cluster.x-k8s.io",
                version="v1alpha1",
                namespace=namespace,
                plural="vclusters",
                name=name
            )
        except client.rest.ApiException as e:
            if e.status == 404:
                existing_resource = None
                pass
            else:
                raise e
        
        if existing_resource:
            vcluster_dict = yaml.safe_load(vcluster) if isinstance(vcluster, str) else vcluster
            resource_version = existing_resource['metadata'].get('resourceVersion')
            vcluster_dict["metadata"]["resourceVersion"] = str(resource_version)

            client.CustomObjectsApi().replace_namespaced_custom_object(
                group="infrastructure.cluster.x-k8s.io",
                version="v1alpha1",
                namespace=namespace,
                plural="vclusters",
                name=name,
                body=vcluster_dict,
            )
            wait_for_service_creation(namespace, name)
            return jsonify({
                "message": "vcluster updated successfully",
                "name": name,
            })
        else:
            createNamespace(namespace)
            client.CustomObjectsApi().create_namespaced_custom_object(
                group="cluster.x-k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="clusters",
                body=yaml.safe_load(custom_resource),
            )
            client.CustomObjectsApi().create_namespaced_custom_object(
                group="infrastructure.cluster.x-k8s.io",
                version="v1alpha1",
                namespace=namespace,
                plural="vclusters",
                body=yaml.safe_load(vcluster),
            )
            client.CoreV1Api().create_namespaced_resource_quota(
                namespace=namespace, body=yaml.safe_load(quota)
            )
            wait_for_service_creation(namespace, name)
            create_ingress(name, namespace, host)
            wait_for_sts_pod_readiness(namespace, name, cluster_id)
            return {
                "message": "vcluster created successfully",
                "name": name,
            }
    except Exception as e:
        logging.error("error occurs while creating cluster :: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

def generate_kubeconfig_usecase(body):
    name = body['name']
    hostClusterId = body["hostClusterId"]
    expirationTime = body["expirationTime"]
    namespace = f"{name}-vcluster"
    secret = get_vault_secret(hostClusterId)
    load_kubernetes_client(secret) 

    secret = client.CoreV1Api().read_namespaced_secret(name=f"{name}-kubeconfig", namespace=namespace)
    kubeconfig = base64.b64decode(secret.data['value']).decode('utf-8')
    kubeconfig_data = yaml.safe_load(kubeconfig)
    server = None
    for cluster in kubeconfig_data.get('clusters', []):
        ser = cluster.get('cluster', {}).get('server')
        if ser:
            server = ser
            break
    print("SERVER :: ", server)    

    cluster_cert = None
    for cluster in kubeconfig_data.get('clusters', []):
        cert = cluster.get('cluster', {}).get('certificate-authority-data')
        if cert:
            cluster_cert = cert
            break

    print(cluster_cert)

    k8sClient = load_kubernetes_client(secret.data['value'])
    vclient = k8sClient.CoreV1Api()
    rbac_v1 = k8sClient.RbacAuthorizationV1Api()

    sa = None
    try:
        sa = vclient.read_namespaced_service_account(name=name, namespace="default")
    except Exception as e:
        if e.status != 404:
            raise

    if not sa:
        service_account = client.V1ServiceAccount(
            metadata=client.V1ObjectMeta(name=name)
        )
        vclient.create_namespaced_service_account(namespace="default", body=service_account)

        cluster_role = client.V1ClusterRole(
            metadata=client.V1ObjectMeta(name=name, namespace="default"),
            rules=[
                client.V1PolicyRule(
                    api_groups=["*"],
                    resources=["*"],
                    verbs=["*"],
                )
            ],
        )
        rbac_v1.create_cluster_role(body=cluster_role)

        cluster_role_binding = client.V1ClusterRoleBinding(
            metadata=client.V1ObjectMeta(name=f"{name}-binding"),
            role_ref=client.V1RoleRef(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name=name,
            ),
            subjects=[
                client.V1Subject(
                    kind="ServiceAccount",
                    name=name,
                    namespace="default",
                )
            ],
        )
        rbac_v1.create_cluster_role_binding(body=cluster_role_binding)
        time.sleep(1)

    token_request = client.AuthenticationV1TokenRequest(
        api_version="authentication.k8s.io/v1",
        kind="TokenRequest",
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1TokenRequestSpec(
            expiration_seconds=expirationTime,
            audiences=["https://kubernetes.default.svc.cluster.local", "k3s"]  
        )
    )
    token_response = vclient.create_namespaced_service_account_token(
        namespace="default",
        name=name,
        body=token_request
    )
    print(token_response)
    token_value = token_response.status.token

    responseData = {
        "cluster": name,
        "clusterCerts": cluster_cert,
        "token": token_value,
        "server": server
    }
    return jsonify(responseData), 200

def check_host_cluster_usecase(body):
    logging.info("Published data: " + json.dumps(body))
    secret_response = []
    for host_cluster_id in body["host_cluster_ids"]:
        secret = get_vault_secret(host_cluster_id)
        secret_response.append({
            "id": host_cluster_id,
            "encoded_config": secret
        })
    best_cluster = get_available_resources_fromSecret(secret_response)
    if best_cluster:
        key = list(best_cluster.keys())[0]
        data = best_cluster[key]
        result = {
            "id": key,
            "best_cpu": data["best_cpu"],
            "best_memory": data["best_memory"]
        }
        return jsonify(result), 200
    else:
        return jsonify({"error": "No available resources"}), 404

def start_cluster_usecase(data):
    logging.info("Published data: " + json.dumps(data))
    received_data = data["data"]
    secret = get_vault_secret(received_data["host_cluster_id"])
    load_kubernetes_client(secret)  
    name = received_data["cluster_name"]
    namespace = f"{name}-vcluster"
    api_client_apps = client.AppsV1Api()

    try:
        vcluster_statefulset = api_client_apps.read_namespaced_stateful_set(
            name=name,
            namespace=namespace
        )
        if vcluster_statefulset.spec.replicas >= 1:
            return jsonify({"message": "cluster already started"}), 200 
        elif vcluster_statefulset.spec.replicas == 0:
            vcluster_statefulset.spec.replicas = 1
            api_client_apps.replace_namespaced_stateful_set(
                name=name,
                namespace=namespace,
                body=vcluster_statefulset
            )
        res = {"message": "cluster starting"}
        logging.info("Cluster started :: ", res)
        return jsonify(res), 200   
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_cluster_status_usecase(body):
    name = body['name']
    hostClusterId = body["hostClusterId"]
    namespace = f"{name}-vcluster"
    secret = get_vault_secret(hostClusterId)
    load_kubernetes_client(secret)  
    status = get_pod_status(namespace, name)
    print("STATUS :: ", status)
    responseData = {
        "status": status
    }
    return jsonify(responseData), 200

def stop_vcluster_usecase(data):
    received_data = data["data"]
    secret = get_vault_secret(received_data["host_cluster_id"])
    load_kubernetes_client(secret)
    name = received_data["cluster_name"]
    api_client_apps = client.AppsV1Api()
    namespace = f"{name}-vcluster"
    try:
        vcluster_statefulset = api_client_apps.read_namespaced_stateful_set(
            name=name,
            namespace=namespace
        )
        if vcluster_statefulset.spec.replicas == 0:
            return jsonify({"message": "cluster already stopped"}), 200 
        elif vcluster_statefulset.spec.replicas >= 1:
            vcluster_statefulset.spec.replicas = 0
            api_client_apps.replace_namespaced_stateful_set(
                name=name,
                namespace=namespace,
                body=vcluster_statefulset
            )
        res = {"message": "cluster stopping"}
        logging.info("Cluster stopping :: ", res)
        return jsonify(res), 200
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def delete_vcluster_usecase(data):
    received_data = data["data"]
    secret = get_vault_secret(received_data["host_cluster_id"])
    load_kubernetes_client(secret)
    name = received_data["cluster_name"]
    namespace = f"{name}-vcluster"
    try:
        v1 = client.CoreV1Api()
        v1.delete_namespace(namespace)
        res = {"message": "cluster deleted"}
        logging.info("Cluster deleted :: ", res)
        return jsonify(res), 204
    except Exception as e:
        print(f"Error deleting namespace '{namespace}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def update_cluster_plan_usecase( data):
    logging.info("Published data: " + json.dumps(data["data"]))
    secret = get_vault_secret(data["data"]["host_cluster_id"])
    load_kubernetes_client(secret) 
    try:
        namespace = data["data"]["cluster"] + "-vcluster"
        logging.info("Subscription data: " + json.dumps(data["data"]["subscription"]))
        subscriptionData = parse_subscription_json(data["data"]["subscription"])
        quota = generate_resource_quota_yaml(subscription=subscriptionData, namespace=namespace) 
        resource_quotas = client.CoreV1Api().list_namespaced_resource_quota(namespace=namespace)
        client.CoreV1Api().create_namespaced_resource_quota(
            namespace=namespace, body=yaml.safe_load(quota)
        )
        for rq in resource_quotas.items:
            resource_quota_name = rq.metadata.name
            try:
                response = client.CoreV1Api().delete_namespaced_resource_quota(name=resource_quota_name, namespace=namespace)
                print(f"Resource Quota '{resource_quota_name}' deleted successfully.")
            except client.rest.ApiException as e:
                if e.status == 404:
                    print(f"Resource Quota '{resource_quota_name}' not found.")
                else:
                    print(f"An error occurred while deleting '{resource_quota_name}':", e)           
        return {
            "message": "vcluster plan upgraded successfully",
        }
    except Exception as e:
        print("Error occurs while updating cluster plan :: ", e)
        raise HTTPException(status_code=500, detail=str(e))

def create_ingress(name: str, namespace: str, host: str):
    print("WE are here for INGRESS")
    networking_v1_api = client.NetworkingV1Api()
    body = client.V1Ingress(
        api_version="networking.k8s.io/v1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(name=name, annotations={
            "nginx.ingress.kubernetes.io/backend-protocol": "HTTPS",
            "nginx.ingress.kubernetes.io/ssl-passthrough": "true",
            "nginx.ingress.kubernetes.io/ssl-redirect": "true",
            "cert-manager.io/cluster-issuer": "letsencrypt-prod"
        }),
        spec=client.V1IngressSpec(
            ingress_class_name="nginx",
            tls=[
                client.V1IngressTLS(
                    hosts=[host],
                    secret_name="tls-secret"
                )
            ],
            rules=[client.V1IngressRule(
                host=host,
                http=client.V1HTTPIngressRuleValue(
                    paths=[client.V1HTTPIngressPath(
                        path="/",
                        path_type="ImplementationSpecific",
                        backend=client.V1IngressBackend(
                            service=client.V1IngressServiceBackend(
                                port=client.V1ServiceBackendPort(
                                    number=443,
                                ),
                                name=name)
                            )
                    )]
                )
            )]
        )
    )
    api_response = networking_v1_api.create_namespaced_ingress(
        namespace=namespace,
        body=body
    )
    print("Ingress created. Status='%s'" % str(api_response.status))

def wait_for_service_creation(namespace, name):
    print("WE are here for WAiting")
    api_client = client.CoreV1Api()
    while True:
        try:
            api_client.read_namespaced_service(name=name, namespace=namespace)
            print(f"Service '{name}' found in namespace '{namespace}'")
            return
        except client.exceptions.ApiException as e:
            if e.status != 404:
                raise
            print(f"Service '{name}' not found, retrying...")
            time.sleep(5)

def wait_for_sts_pod_readiness(namespace, name, clusterId):
    try:
        core_v1 = client.CoreV1Api()
        timeout = 300 
        start_time = time.time()
        while True:
            pods = core_v1.list_namespaced_pod(namespace, field_selector=f"metadata.name={name}").items
            all_ready = all(p.status.phase == "Running" for p in pods)
            if all_ready:
                labels = {
                    "status-controller-vcluster": "cluster-manager",
                    "status-controller": clusterId
                }
                add_labels_to_statefulset(namespace, name, labels)
                return True
            if time.time() - start_time > timeout:
                return False
            time.sleep(5)
    except Exception as e:
        return f"An error occurred: {e}"

    # Parse the request body
    body = request.json
    name = body['name']
    host_cluster_id = body["hostClusterId"]
    expiration_time = body["expirationTime"]
    namespace = f"{name}-vcluster"

    secret = get_vault_secret(host_cluster_id)
    load_kubernetes_client(secret)
    secret_data = client.CoreV1Api().read_namespaced_secret(
        name=f"{name}-kubeconfig", namespace=namespace
    )
    kubeconfig = base64.b64decode(secret_data.data['value']).decode('utf-8')
    kubeconfig_data = yaml.safe_load(kubeconfig)
    server = None
    for cluster in kubeconfig_data.get('clusters', []):
        server = cluster.get('cluster', {}).get('server')
        if server:
            break

    print("SERVER:", server)
    cluster_cert = None
    for cluster in kubeconfig_data.get('clusters', []):
        cluster_cert = cluster.get('cluster', {}).get('certificate-authority-data')
        if cluster_cert:
            break

    print("Cluster Certificate:", cluster_cert)
    # Load Kubernetes client
    k8s_client = load_kubernetes_client(secret_data.data['value'])
    vclient = k8s_client.CoreV1Api()
    rbac_v1 = k8s_client.RbacAuthorizationV1Api()
    # Check if the service account exists
    try:
        sa = vclient.read_namespaced_service_account(name=name, namespace="default")
    except client.exceptions.ApiException as e:
        if e.status != 404:
            raise
        sa = None
    if not sa:
        # Create the ServiceAccount
        service_account = client.V1ServiceAccount(
            metadata=client.V1ObjectMeta(name=name)
        )
        vclient.create_namespaced_service_account(namespace="default", body=service_account)
        # Create the ClusterRole
        cluster_role = client.V1ClusterRole(
            metadata=client.V1ObjectMeta(name=name, namespace="default"),
            rules=[
                client.V1PolicyRule(
                    api_groups=["*"],
                    resources=["*"],
                    verbs=["*"],
                )
            ],
        )
        rbac_v1.create_cluster_role(body=cluster_role)
        # Create the ClusterRoleBinding
        cluster_role_binding = client.V1ClusterRoleBinding(
            metadata=client.V1ObjectMeta(name=f"{name}-binding"),
            role_ref=client.V1RoleRef(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name=name,
            ),
            subjects=[
                client.V1Subject(
                    kind="ServiceAccount",
                    name=name,
                    namespace="default",
                )
            ],
        )
        rbac_v1.create_cluster_role_binding(body=cluster_role_binding)
        time.sleep(1)

    # Create token request
    token_request = client.V1TokenRequest(
        api_version="authentication.k8s.io/v1",
        kind="TokenRequest",
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1TokenRequestSpec(
            expiration_seconds=expiration_time,
            audiences=["https://kubernetes.default.svc.cluster.local", "k3s"]
        )
    )
    token_response = vclient.create_namespaced_service_account_token(
        namespace="default",
        name=name,
        body=token_request
    )
    token_value = token_response.status.token

    # Prepare the response
    response_data = {
        "cluster": name,
        "clusterCerts": cluster_cert,
        "token": token_value,
        "server": server
    }
    return jsonify(response_data), 200
def delete_vcluster_usecase():
    received_data = request.json["data"]
    secret = get_vault_secret(received_data["host_cluster_id"])
    # Create the Kubernetes client
    load_kubernetes_client(secret)
    name = received_data["cluster_name"]
    namespace = f"{name}-vcluster"
    try:
        v1 = client.CoreV1Api()
        v1.delete_namespace(namespace)
        res = {"message": "cluster deleted"}
        logging.info("Cluster deleted :: ",res)
        return jsonify(res),204
    except Exception as e:
        print(f"Error deleting namespace '{namespace}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))   
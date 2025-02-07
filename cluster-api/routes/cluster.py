import json
import logging
import os
from fastapi import APIRouter, Body, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from dapr.clients import DaprClient
import requests
from typing import List

from dto.cluster_request import ClusterRequest
from dto.cluster_response import ClusterResponse
from dto.cluster_upgrade import ClusterUpgradeRequest
from middleware.middleware import is_authenticated
from models.cluster import Cluster
from models.common_response import ResponseModel
from models.generate_kubeconfig import GenerateKubeconfig
from schemas.cluster_schema import clusters_serializer, is_valid_url_name
from schemas.host_cluster_schema import host_clusters_serializer_test
from schemas.subscription_schema import subscription_from_dict
from utills.common_utills import extract_time_components, get_best_cluster
from models.user import User
from utills.common_response import debug_response, generate_response

router = APIRouter()

@router.post("", response_description="Create a cluster", status_code=status.HTTP_201_CREATED, response_model={})
def create_Cluster(request: Request, clusterRequest: ClusterRequest = Body(...)):
    name_status, error_message = is_valid_url_name(clusterRequest.name)
    authorization_header = request.headers.get("Authorization", "")
    token = authorization_header.split("Bearer ")[1]
    user_info = is_authenticated(token)
    # checking create 'create-cluster' role is assign to the user.
    if user_info and 'realm_access' in user_info:
        realm_roles = user_info['realm_access']['roles']
        if 'create-cluster' not in realm_roles:
            # If the user does not have the 'create-cluster' role
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not allowed to create clusters")
    if name_status is False and error_message is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
    createdCluster = request.app.database["cluster"].find_one({"name": clusterRequest.name})
    if createdCluster is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cluster with name {clusterRequest.name} already exist")
    subscription = request.app.database["subscription"].find_one({"_id": clusterRequest.subscriptionId})
    if subscription is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscription with ID {clusterRequest.subscriptionId} not found")
    host_cluster_reponse = request.app.database["hostCluster"].find({"region": clusterRequest.region})
    hostClusters = host_clusters_serializer_test(json.dumps(list(host_cluster_reponse)))
    if len(list(hostClusters)) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostCluster not found within the region {clusterRequest.region}")
    
    host_cluster_ids = list(map(lambda x: x['id'], hostClusters))

    best_cluster_id = get_best_cluster(host_cluster_ids)
    best_cluster_name = ""
    for obj in hostClusters:
        if obj['id'] == best_cluster_id:
            best_cluster_name = obj['name']
    if best_cluster_name == "":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"hostCluster not found within the region {clusterRequest.region}")

    user_obj: User = request.state.user

    cluster = Cluster(
        name=clusterRequest.name,
        userId=user_obj.id,
        status="Creating",
        hostClusterId=best_cluster_id,
        subscriptionId=clusterRequest.subscriptionId,
        kube_version=clusterRequest.kube_version,
    )
    clusterPayload = jsonable_encoder(cluster)
    new_cluster = request.app.database["cluster"].insert_one(clusterPayload)
    create_cluster = request.app.database["cluster"].find_one(
        {"_id": new_cluster.inserted_id}
    )
    created_cluster = clusters_serializer(create_cluster)
    try:
        with DaprClient() as client:
            del subscription["_id"]
            payload = {
                "subscription": subscription,
                "host_cluster_id": best_cluster_id,
                "host_cluster_name": best_cluster_name,
                "cluster": created_cluster
            }
            client.publish_event(
                pubsub_name="messagebus",
                topic_name="cluster-create",
                data=json.dumps(payload),
                data_content_type="application/json",
            )
            logging.info("Published data from create cluster :: %s", str(payload))
        return{"success": True,
        "code": status.HTTP_200_OK,
        "message": "Clusters listed successfully",
        "data": created_cluster
        }
    except Exception as e:
        debug_response(e, "Error occurs on creating cluster", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create cluster", None)

@router.put("/upgrade/{id}", response_description="Update a cluster", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def update_cluster(id: str, request: Request, clusterUpgradeRequest: ClusterUpgradeRequest = Body(...)):
    kube_version = clusterUpgradeRequest.kube_version
    cluster = request.app.database["cluster"].find_one({"_id": id})
    if cluster is None:
        return generate_response(False, status.HTTP_404_NOT_FOUND, f"Cluster with ID {id} not found", None)

    current_version_parts = list(map(int, cluster["kube_version"].split("v")[1].split(".")))
    new_version_parts = list(map(int, kube_version.split("v")[1].split(".")))

    if new_version_parts <= current_version_parts:
        return generate_response(False, status.HTTP_400_BAD_REQUEST, "Kube version can only be upgraded", None)

    host_data = request.app.database["hostCluster"].find_one({"_id": cluster["host_cluster_id"]})
    if host_data is None:
        return generate_response(False, status.HTTP_404_NOT_FOUND, "Host cluster data not found", None)

    subscription = request.app.database["subscription"].find_one({"_id": cluster["subscription_id"]})
    if subscription is None:
        return generate_response(False, status.HTTP_404_NOT_FOUND, f"Subscription with ID {cluster['subscription_id']} not found", None)

    request.app.database["cluster"].update_one(
        {"_id": id},
        {"$set": {"kube_version": kube_version, "status": "Updating"}}
    )

    find_cluster = request.app.database["cluster"].find_one({"_id": id})
    update_cluster = clusters_serializer(find_cluster)
    try:
        # Prepare and publish the event to Dapr
        with DaprClient() as client:
            del subscription["_id"]
            payload = {
                "subscription": subscription,
                "host_cluster_id": cluster["host_cluster_id"],
                "host_cluster_name": host_data["name"],
                "cluster": update_cluster,
            }
            client.publish_event(
                pubsub_name="messagebus",
                topic_name="cluster-create",
                data=json.dumps(payload),
                data_content_type="application/json",
            )
            logging.info("Published data for cluster update: %s", payload)
        return generate_response(True, status.HTTP_200_OK, "Cluster updated successfully", update_cluster)
    except Exception as e:
        debug_response(e, "Error occurs on updating cluster", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to update cluster", None)

@router.post("/generate-config", response_description="Generate KubeConfig", status_code=status.HTTP_200_OK)
def generate_kube_config(request: Request, generateKubeconfig: GenerateKubeconfig = Body(...)):

    if extract_time_components(generateKubeconfig.expiryTime) is None:
        return generate_response(False, status.HTTP_400_BAD_REQUEST, "Incorrect expiration time format", [])
    
    expirationTime = extract_time_components(generateKubeconfig.expiryTime)

    if expirationTime < 600:
        return generate_response(False, status.HTTP_400_BAD_REQUEST, "Expiration time shouldn't be less than 10 min", [])

    clusterId = generateKubeconfig.clusterId
    cluster = request.app.database["cluster"].find_one({"_id": clusterId})
    if cluster is None:
        return generate_response(False, status.HTTP_404_NOT_FOUND, f"Cluster with ID {clusterId} not found", [])

    name = cluster["name"]
    hostClusterId = cluster["host_cluster_id"]

    payload = {
        "name": name,
        "hostClusterId": hostClusterId,
        "expirationTime": expirationTime
    }
    baseUrl = os.getenv('SERVICE_URL')

    response = requests.post(baseUrl + "/generate-config", json=payload)
    if response.status_code == 200:  # Check if the request was successful
        debug_response(response.json(), "Response from generate-config", "info")
        responseBody = response.json()
        with open('file/kubeconfig') as f:
            kubeconfig_file = f.read().format(cluster=responseBody["cluster"], clusterCerts=responseBody["clusterCerts"], token=responseBody["token"], server=responseBody["server"])

            response = Response(content=kubeconfig_file, media_type='text/yaml')
            response.headers['Content-Disposition'] = f'attachment; filename=kubeconfig.yaml'
            return response
    else:
        debug_response(response.json(), "Error occurs on generating kubeconfig", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error", [])

@router.get("/{id}", response_description="Get a cluster by id", response_model={})
def find_cluster(id: str, request: Request):
    try:
        cluster = request.app.database["cluster"].find_one({"_id": id})
        if cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"Cluster with ID {id} not found", None)

        user = request.app.database["user"].find_one({"_id": cluster["user_id"]})
        if user is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"User with ID {id} not found", None)

        subscription = request.app.database["subscription"].find_one({"_id": cluster["subscription_id"]})
        if subscription is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"Subscription with ID {id} not found", None )

        host_cluster = request.app.database["hostCluster"].find_one({"_id": cluster["host_cluster_id"]})
        if host_cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"HostCluster with ID {id} not found", None)

        response = ClusterResponse(
            id=cluster["_id"],
            name=cluster["name"],
            status=cluster["status"],
            created=cluster["created"],
            kube_version=cluster["kube_version"],
            user=user,
            subscription=subscription,
            hostCluster=host_cluster
        )
        return{"success": True,
        "code": status.HTTP_200_OK,
        "message": "Clusters found successfully",
        "data": response
        }
    except Exception as e:
        debug_response(e, "Error occurs on retrieving cluster", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to retrieve cluster", None)

def get_and_update_status_async(clusters: List[ClusterResponse], request: Request,response_model: ResponseModel):
    for cluster in clusters:
        try:
            status = get_status(cluster.name, cluster.hostCluster.id)
            if status.status_code == 200:
                print("STATUS :: ", status.json()["status"])
                # Define the filter to identify the document you want to update
                filter = {"_id": cluster.id}

                # Define the update operation using $set to update a single field
                update = {"$set": {"status": status.json()["status"]}}
                request.app.database["cluster"].update_one(filter, update)
                return generate_response(True, status.HTTP_200_OK, "Cluster status updated", [])
        except Exception as e:
            debug_response(e, "Error occurs on fetching status of cluster", "error")
            return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to fetch status of cluster", [])

@router.get("", response_description="List all cluster", response_model={})
def list_Clusters(request: Request):
    try:
        user_obj: User = request.state.user
        print("USER_OBJ :: ", user_obj.id)
        clusters = list(request.app.database["cluster"].find({"user_id": user_obj.id}).limit(10))
        print("Clusters :: ", clusters)
        responses = []
        for cluster in clusters:
            host_cluster = request.app.database["hostCluster"].find_one({"_id": cluster["host_cluster_id"]})
            subscription = request.app.database["subscription"].find_one({"_id": cluster["subscription_id"]})
            if host_cluster is not None and subscription is not None:
                response = ClusterResponse(
                    id=cluster["_id"],
                    subscription=subscription,
                    user=user_obj,
                    created=cluster["created"],
                    status=cluster["status"],
                    name=cluster["name"],
                    kube_version=cluster["kube_version"],
                    hostCluster=host_cluster
                )
                responses.append(response)
        return{"success": True,
        "code": status.HTTP_200_OK,
        "message": "Clusters listed successfully",
        "data": responses
        }
    except Exception as e:
        debug_response(e, "Error occurs on listing clusters", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to list clusters", [])

@router.get("/{id}/status", response_description="Get a cluster by id", response_model=ResponseModel)
def get_cluster_status(id: str, request: Request):
    try:
        cluster = request.app.database["cluster"].find_one({"_id": id})
        if cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"Cluster with ID {id} not found", None)

        user = request.app.database["user"].find_one({"_id": cluster["user_id"]})
        if user is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"User with ID {id} not found", None)

        host_cluster = request.app.database["hostCluster"].find_one({"_id": cluster["host_cluster_id"]})
        if host_cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"HostCluster with ID {id} not found", None)

        response = get_status(cluster["name"], host_cluster["_id"])
        if response.status_code == 200:
            return generate_response(True, status.HTTP_200_OK, "Cluster status retrieved", response.json())
        else:
            return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error", None)
    except Exception as e:
        debug_response(e, "Error occurs on retrieving cluster status", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to retrieve cluster status", None)

def get_status(name: str, hostClusterId):
    payload = {
        "name": name,
        "hostClusterId": hostClusterId,
    }
    baseUrl = os.getenv('SERVICE_URL')
    return requests.post(baseUrl + "/host-cluster/cluster/status", json=payload)

@router.patch("/{id}/start", response_description="Start cluster by id", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def start_cluster(id: str, request: Request):
    try:
        cluster = request.app.database["cluster"].find_one({"_id": id})
        if cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"Cluster with ID {id} not found", None)

        host_cluster = request.app.database["hostCluster"].find_one({"_id": cluster["host_cluster_id"]})
        if host_cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"HostCluster with ID {id} not found", None)

        with DaprClient() as client:
            payload = {
                "host_cluster_id": host_cluster["_id"],
                "cluster_name": cluster["name"]
            }
            client.publish_event(
                pubsub_name="messagebus",
                topic_name="cluster-start",
                data=json.dumps(payload),
                data_content_type="application/json",
            )
            logging.info("Published data: " + json.dumps(payload))
            debug_response(payload, "Published data", "info")
        return generate_response(True, status.HTTP_200_OK, "Sent command for starting cluster", None)
    except Exception as e:
        debug_response(e, "Error occurs on starting cluster", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to start cluster", None)

@router.patch("/{id}/stop", response_description="Stop cluster by id", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def stop_cluster(id: str, request: Request):
    try:
        cluster = request.app.database["cluster"].find_one({"_id": id})
        if cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"Cluster with ID {id} not found", None)

        host_cluster = request.app.database["hostCluster"].find_one({"_id": cluster["host_cluster_id"]})
        if host_cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"HostCluster with ID {id} not found", None)

        with DaprClient() as client:
            payload = {
                "host_cluster_id": host_cluster["_id"],
                "cluster_name": cluster["name"]
            }
            client.publish_event(
                pubsub_name="messagebus",
                topic_name="cluster-stop",
                data=json.dumps(payload),
                data_content_type="application/json",
            )
            logging.info("Published data: " + json.dumps(payload))
            debug_response(payload, "Published data", "info")
        return generate_response(True, status.HTTP_200_OK, "Sent command for stopping cluster", None)
    except Exception as e:
        debug_response(e, "Error occurs on stopping cluster", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to stop cluster", None)

@router.delete("/{id}", response_description="Delete cluster by id", status_code=status.HTTP_202_ACCEPTED, response_model=ResponseModel)
def delete_cluster(id: str, request: Request, response: Response):
    try:
        cluster = request.app.database["cluster"].find_one({"_id": id})
        if cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"Cluster with ID {id} not found", None)

        host_cluster = request.app.database["hostCluster"].find_one({"_id": cluster["host_cluster_id"]})
        if host_cluster is None:
            return generate_response(False, status.HTTP_404_NOT_FOUND, f"HostCluster with ID {id} not found", None)

        delete_result = request.app.database["cluster"].delete_one({"_id": id})
        if delete_result.deleted_count == 1:
            try:
                with DaprClient() as client:
                    payload = {
                        "host_cluster_id": host_cluster["_id"],
                        "cluster_name": cluster["name"]
                    }
                    client.publish_event(
                        pubsub_name="messagebus",
                        topic_name="cluster-delete",
                        data=json.dumps(payload),
                        data_content_type="application/json",
                    )
                return generate_response(True, status.HTTP_202_ACCEPTED, f"Cluster with ID {id} deleted", None)
            except Exception as e:
                debug_response(e, "Error occurs on publishing delete event", "error")
                return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to publish delete event", None)
        return generate_response(False, status.HTTP_404_NOT_FOUND, f"Cluster with ID {id} not found", None)
    except Exception as e:
        debug_response(e, "Error occurs on deleting cluster", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to delete cluster", None)

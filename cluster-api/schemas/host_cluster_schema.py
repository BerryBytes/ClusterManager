import json

from pyparsing import Any
from dto.host_cluster_request import HostClusterRequest

from models.host_cluster import HostCluster


def host_cluster_serializer(hostCluster) -> dict:
    return {
        "id": str(hostCluster["_id"]),
        "name": hostCluster["name"],
        "region": hostCluster["region"],
        "provider": hostCluster["provider"],
        "user_id": hostCluster["user_id"],
        "nodes": hostCluster["nodes"],
        "active": hostCluster["active"],
        "version": hostCluster["version"],
        "created": hostCluster["created"],
        "updated": hostCluster["updated"],
    }


def host_clusters_serializer(cursor) -> list:
    return [host_cluster_serializer(hostCluster) for hostCluster in cursor]


def host_clusters_serializer_test(data):
    # Convert JSON data to Python object
    python_object = json.loads(data)
    response = []
    for res in python_object:
        response.append({
            "id": res["_id"],
            "name": res["name"],
            "region": res["region"],
            "provider": res["provider"],
            "nodes": res["nodes"],
            "active": res["active"],
            "version": res["version"],
            "created": res["created"],
            "updated": res["updated"],
            "user_id": res["user_id"],
        })

    return response


def host_Cluster_from_dict(res: HostClusterRequest, user_id: str):
    return HostCluster(
        name=res.name,
        region=res.region,
        provider=res.provider,
        nodes=res.nodes,
        active=res.active,
        version=res.version,
        userId=user_id,
    )

"""
Module for host cluster serialization and conversion.

Provides functions to serialize single or multiple host clusters,
convert JSON data to Python objects, and create host_cluster models
from host_cluster_request DTOs.
"""

import json

from dto.host_cluster_request import HostClusterRequest
from models.host_cluster import HostCluster
from pyparsing import Any


def host_cluster_serializer(hostCluster) -> dict:
    """Serialize a single host cluster for output."""
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
    """Serialize a list of host clusters."""
    return [host_cluster_serializer(hostCluster) for hostCluster in cursor]


def host_clusters_serializer_test(data):
    """Convert JSON data to serialized host cluster list."""
    python_object = json.loads(data)
    response = []
    for res in python_object:
        response.append(
            {
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
            }
        )

    return response


def host_Cluster_from_dict(res: HostClusterRequest, user_id: str):
    """Convert host_cluster_request to host_cluster model."""
    return HostCluster(
        name=res.name,
        region=res.region,
        provider=res.provider,
        nodes=res.nodes,
        active=res.active,
        version=res.version,
        userId=user_id,
    )

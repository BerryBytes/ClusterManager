"""
Host Cluster API Routes.

This module defines FastAPI routes for creating, listing, retrieving,
and deleting host clusters. It handles validation, authentication,
database operations, and response formatting.
"""

import logging
from typing import List

from dto.host_cluster_request import HostClusterRequest
from fastapi import APIRouter, Body, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.common_response import ResponseModel
from models.host_cluster import HostCluster
from models.user import User
from schemas.cluster_schema import is_valid_url_name
from schemas.host_cluster_schema import host_Cluster_from_dict
from utills.common_response import debug_response, generate_response

router = APIRouter()


@router.post(
    "/",
    response_description="Create a cluster",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseModel,
)
def create_Cluster(request: Request, clusterRequest: HostClusterRequest = Body(...)):
    """
    Create a new host cluster.

    Validates the cluster name, associates it with the authenticated user,
    inserts it into the database, and returns the created object.
    """
    name_status, error_message = is_valid_url_name(clusterRequest.name)
    if not name_status and error_message is not None:
        return generate_response(
            False,
            status.HTTP_400_BAD_REQUEST,
            f"Failed to create host cluster {error_message}",
            None,
        )
    try:
        user_obj: User = request.state.user
        host_cluster_obj = host_Cluster_from_dict(clusterRequest, user_obj.id)
        new_cluster = request.app.database["hostCluster"].insert_one(
            jsonable_encoder(host_cluster_obj)
        )
        created_cluster = request.app.database["hostCluster"].find_one(
            {"_id": new_cluster.inserted_id}
        )
        return generate_response(
            True,
            status.HTTP_201_CREATED,
            "Host cluster created successfully",
            created_cluster,
        )
    except Exception as e:
        debug_response(e, "Error occurs on adding host cluster", "error")
        return generate_response(
            False,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to create host cluster",
            None,
        )


@router.get(
    "/", response_description="List all host cluster", response_model=ResponseModel
)
def list_host_cluster(request: Request):
    """
    Retrieve a list of all host clusters.

    Returns a list of up to 100 host clusters from the database.
    """
    try:
        hostCluster = list(request.app.database["hostCluster"].find(limit=100))
        return generate_response(
            True, status.HTTP_200_OK, "List all host clusters", hostCluster
        )
    except Exception as e:
        debug_response(e, "Error occurs on listing host clusters", "error")
        return generate_response(
            False,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to list host clusters",
            None,
        )


@router.get(
    "/{id}",
    response_description="Get a single host cluster by id",
    response_model=ResponseModel,
)
def find_host_cluster(id: str, request: Request):
    """
    Retrieve a host cluster by its ID.

    Returns the host cluster data if found, otherwise a 404 error.
    """
    try:
        host_cluster = request.app.database["hostCluster"].find_one({"_id": id})
        if host_cluster is not None:
            return generate_response(
                True, status.HTTP_200_OK, "Host cluster found", host_cluster
            )
        return generate_response(
            False,
            status.HTTP_404_NOT_FOUND,
            f"Host cluster with ID {id} not found",
            None,
        )
    except Exception as e:
        debug_response(e, "Error occurs on retrieving host cluster", "error")
        return generate_response(
            False,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to retrieve host cluster",
            None,
        )


@router.delete("/{id}", response_description="Delete a host cluster")
def delete_subscription(id: str, request: Request, response: ResponseModel):
    """
    Delete a host cluster by its ID.

    Removes the cluster from the database and returns success or not found response.
    """
    try:
        delete_result = request.app.database["hostCluster"].delete_one({"_id": id})
        if delete_result.deleted_count == 1:
            return generate_response(
                True,
                status.HTTP_204_NO_CONTENT,
                f"Host cluster with ID {id} deleted",
                None,
            )
        return generate_response(
            False,
            status.HTTP_404_NOT_FOUND,
            f"Host cluster with ID {id} not found",
            None,
        )
    except Exception as e:
        debug_response(e, "Error occurs on deleting host cluster", "error")
        return generate_response(
            False,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to delete host cluster",
            None,
        )

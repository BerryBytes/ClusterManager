import uuid
from fastapi import APIRouter, Body, Request, HTTPException, status, Response
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import logging
from bson import ObjectId
from typing import List
from dto.kube_version_request import KubeVersionRequest
from models.common_response import ResponseModel
from models.kube_version import KubeVersion
from utills.common_response import debug_response, generate_response

router = APIRouter()

# Create a new kubeversion
@router.post("/", response_description="Create a kubeversion", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
def create_kubeversion(request: Request, clusterRequest: KubeVersionRequest = Body(...)):
    debug_response(clusterRequest.dict(), "Received request body", "debug")
    try:
        kubeversion_data = jsonable_encoder(clusterRequest)
        kubeversion_data["_id"] = str(uuid.uuid4())  # Generate a UUID and use it as the _id
        debug_response(kubeversion_data)
        new_kubeversion = request.app.database["kubeversion"].insert_one(kubeversion_data)
        inserted_kubeversion = request.app.database["kubeversion"].find_one({"_id": new_kubeversion.inserted_id})
        if inserted_kubeversion:
            inserted_kubeversion["_id"] = str(inserted_kubeversion["_id"])
        return generate_response(True, status.HTTP_201_CREATED, "Kubeversion created successfully", inserted_kubeversion)
    except Exception as e:
        debug_response(e, "Error occurs on creating kubeversion", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create kubeversion", None)

# List all kubeversions
@router.get("/", response_description="List all kubeversion", response_model=ResponseModel)
def list_kubeversions(request: Request):
    try:
        kubeversions = list(request.app.database["kubeversion"].find(limit=100))
        for kubeversion in kubeversions:
            kubeversion["_id"] = str(kubeversion["_id"])
        return generate_response(True, status.HTTP_200_OK, "List all kubeversions", kubeversions)
    except Exception as e:
        debug_response(e, "Failed to retrieve kubeversions", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error", [])

# Update an existing kubeversion
@router.put("/{id}", response_description="Update kubeversion", response_model=ResponseModel)
def update_kubeversion(id: str, request: Request, clusterRequest: KubeVersionRequest = Body(...)):
    try:
        kubeversion_data = jsonable_encoder(clusterRequest)
        update_result = request.app.database["kubeversion"].update_one({"_id": ObjectId(id)}, {"$set": kubeversion_data})
        if update_result.matched_count == 0:
            debug_response(e, "Failed to retrieve kubeversions", "error")
            return generate_response(True, status.HTTP_404_NOT_FOUND, f"kubeversion with ID {id} not found", None)

        updated_kubeversion = request.app.database["kubeversion"].find_one({"_id": ObjectId(id)})
        if updated_kubeversion:
            updated_kubeversion["_id"] = str(updated_kubeversion["_id"])
        return generate_response(True, status.HTTP_202_ACCEPTED, f"kubeversion with {id} updated", updated_kubeversion)
    except Exception as e:
        debug_response(e, "Error occurs on updating kubeversion", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error", None)

# Delete a kubeversion
@router.delete("/{id}", response_description="Delete kubeversion", response_model=ResponseModel)
def delete_kubeversion(id: str, request: Request, response: Response):
    try:
        delete_result = request.app.database["kubeversion"].delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            response.status_code = status.HTTP_204_NO_CONTENT
            debug_response(id, "kubeversion deleted", "info")
            return generate_response(True, status.HTTP_202_ACCEPTED, f"kubeversion with {id} deleted", response)
        return generate_response(True, status.HTTP_404_NOT_FOUND, "kubeversion with ID {id} not found", None)
    except Exception as e:
        debug_response(e, "Error occurs on deleting kubeversion", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error", None)

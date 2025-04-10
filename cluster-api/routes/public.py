import os
import asyncio
from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from dto.cluster_status_request import ClusterStatusRequest
from keycloak import KeycloakOpenID
from models.common_response import ResponseModel
from models.subscription import Subscription
from models.user import UserLogin
from utills.common_response import debug_response, generate_response
from routes.websocket import broadcast_message  # Import the broadcast function

router = APIRouter()

@router.get("/subscriptions", response_description="List all subscriptions", response_model=ResponseModel)
def list_subscription(request: Request):
    try:
        subscriptions = list(request.app.database["subscription"].find(limit=100))
        res = generate_response(
            success=True,
            code=status.HTTP_200_OK,
            message="List all subscriptions",
            data=subscriptions
        )
        return res

    except Exception as e:
        debug_response(e)
        return generate_response(
            success=False,
            code=HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR),
            message="Failed to retrieve subscriptions",
            data=[]
        )

@router.patch("/cluster-status", response_description="Post pod Status", status_code=status.HTTP_200_OK, response_model={})
def update_cluster_status(request: Request, data: ClusterStatusRequest = Body(...)):
    try:
        cluster = request.app.database["cluster"].find_one({"_id": data.id})
        if cluster is None:
            return generate_response(
                success=False,
                code=status.HTTP_404_NOT_FOUND,
                message=f"Cluster with ID {data.id} not found",
                data=None
            )
        filter = {"_id": data.id}
        update = {"$set": {"status": data.status}}
        request.app.database["cluster"].update_one(filter, update)
        user_id = cluster["user"].get("id")

        # Broadcast WebSocket message
        message = {
            "event": "cluster_status_updated",
            "cluster_id": data.id,
            "status": data.status
        }
        # Call the broadcast function asynchronously
        asyncio.create_task(broadcast_message(message))

        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Cluster status updated successfully",
            "data": data
        }
    except Exception as e:
        debug_response(e, "Error occurs on updating cluster status", "error")
        return generate_response(
            success=False,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to update cluster status",
            data=None
        )

@router.post("/login", response_description="Login", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def login( data: UserLogin = Body(...)):
    try:
        debug_response(data.dict(), "Received request body", "debug")
        keycloak_openid = KeycloakOpenID(
            server_url=os.getenv('KEYCLOAK_URL'),
            realm_name=os.getenv('REALM_NAME'),
            client_id=os.getenv('CLIENT_ID'),
        )
        token = keycloak_openid.token(data.userName, data.password)
        debug_response(token, "Received token", "debug")
        return generate_response(
            success=True,
            code=status.HTTP_200_OK,
            message="Login successful",
             data=token
        )
    except Exception as e:
        debug_response(e, "Error occurs on login", "error")
        return generate_response(
            success=False,
            code=status.HTTP_401_UNAUTHORIZED,
            message="Failed to login",
            data=None
        )

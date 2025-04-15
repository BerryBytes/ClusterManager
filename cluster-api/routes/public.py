from datetime import datetime
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
from routes.websocket import send_message_to_user, broadcast_message  # Import both functions

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

@router.patch("/cluster-status", response_description="Post pod Status", status_code=status.HTTP_200_OK)
async def update_cluster_status(request: Request, data: ClusterStatusRequest = Body(...)):
    """Update cluster status and notify the cluster owner via WebSocket."""
    try:
        # Input validation
        if not data.id:
            return generate_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Cluster ID is required",
                data=None
            )
            
        if not data.status:
            return generate_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Status is required",
                data=None
            )
        
        # Find cluster by ID
        cluster = request.app.database["cluster"].find_one({"_id": data.id})
        if cluster is None:
            return generate_response(
                success=False,
                code=status.HTTP_404_NOT_FOUND,
                message=f"Cluster with ID {data.id} not found",
                data=None
            )
        
        # Update cluster status in database
        filter = {"_id": data.id}
        update = {"$set": {"status": data.status, "updated_at": datetime.utcnow()}}
        update_result = request.app.database["cluster"].update_one(filter, update)
        
        if update_result.modified_count == 0:
            # No changes were made
            print(f"No changes made to cluster {data.id} status")
        
        # Extract user_id from cluster document
        user_id = None
        if "user_id" in cluster:
            user_id = cluster["user_id"]
        elif "user" in cluster and isinstance(cluster["user"], dict) and "id" in cluster["user"]:
            user_id = cluster["user"]["id"]
            
        # Send WebSocket notification if we have a user ID
        notification_sent = False
        if user_id:
            # Create WebSocket message
            message = {
                "event": "cluster_status_updated",
                "cluster_id": data.id,
                "cluster_name": cluster.get("name", ""),
                "status": data.status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send message to user
            notification_sent = await send_message_to_user(user_id, message)
            print(f"WebSocket notification {'sent' if notification_sent else 'not sent'} to user {user_id}")
        
        # Return success response
        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Cluster status updated successfully",
            "data": {
                "id": data.id,
                "status": data.status,
                "notification_sent": notification_sent
            }
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

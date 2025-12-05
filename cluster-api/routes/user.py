"""
User API Routes with Keycloak Integration.

Provides endpoints to list users, verify tokens,
check subscriptions, and request subscriptions.
"""

import os
from typing import List

import requests
from fastapi import APIRouter, Body, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from keycloak import KeycloakAdmin, KeycloakOpenID
from middleware.middleware import is_authenticated
from models.common_response import ResponseModel
from models.user import User, UserLogin
from utills.common_response import debug_response, generate_response

router = APIRouter()

# Define your Keycloak configuration & constant values
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")
ADMIN_CLIENT_ID = os.getenv("ADMIN_CLIENT_ID")
ADMIN_CLIENT_SECRET = os.getenv("ADMIN_CLIENT_SECRET")
REQUEST_GROUP_NAME = os.getenv("REQUEST_GROUP_NAME")

# Initialize KeycloakOpenID
keycloak_admin = KeycloakAdmin(
    server_url=KEYCLOAK_URL,
    client_id=ADMIN_CLIENT_ID,
    realm_name=REALM_NAME,
    client_secret_key=ADMIN_CLIENT_SECRET,
)


@router.get("/", response_description="List all users", response_model=ResponseModel)
def list_user(request: Request):
    """Retrieve a list of all users from the database."""
    try:
        users = list(request.app.database["user"].find(limit=100))
        return generate_response(True, status.HTTP_200_OK, "List of users", users)
    except Exception as e:
        debug_response(e, "Error occurs on listing users", "error")
        return generate_response(
            False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to list users", []
        )


@router.get(
    "/subscription-check",
    response_description="subscription check",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResponseModel,
)
def subscription_check(request: Request):
    """
    Check subscription status and Keycloak groups/roles
    for the authenticated user.
    """
    try:
        authorization_header = request.headers.get("Authorization", "")
        token = authorization_header.split("Bearer ")[1]
        user_info = is_authenticated(token)
        user_groups = keycloak_admin.get_user_groups(user_id=user_info["sub"])
        user = request.app.database["user"].find_one({"email": user_info["email"]})
        response = {
            "user_id": user["_id"],
            "username": user_info["name"],
            "email": user_info["email"],
            "user_groups": user_groups,
            "realm_roles": user_info["realm_access"]["roles"],
        }
        return generate_response(
            True, status.HTTP_202_ACCEPTED, "Subscription check successful", response
        )
    except Exception as e:
        debug_response(e, "Error occurs on subscription check", "error")
        return generate_response(
            False, status.HTTP_400_BAD_REQUEST, "Failed to check subscription", []
        )


@router.get(
    "/{id}",
    response_description="Get a single user by id",
    response_model=ResponseModel,
)
def find_user(id: str, request: Request):
    """Retrieve a single user by ID."""
    try:
        user = request.app.database["user"].find_one({"_id": id})
        if user is not None:
            return generate_response(True, status.HTTP_200_OK, "User found", [user])
        return generate_response(
            False, status.HTTP_404_NOT_FOUND, f"User with ID {id} not found", []
        )
    except Exception as e:
        debug_response(e, "Error occurs on retrieving user", "error")
        return generate_response(
            False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to retrieve user", []
        )


@router.post(
    "/ping", response_description="verified_user", status_code=status.HTTP_202_ACCEPTED
)
def ping_user():
    """Simple endpoint to verify service availability."""
    return generate_response(True, status.HTTP_202_ACCEPTED, "Ping successful", [])


@router.post(
    "/verify-token",
    response_description="verified_user",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResponseModel,
)
def token_verify(request: Request):
    """Verify JWT token and check if the user has 'create-cluster' role."""
    try:
        authorization_header = request.headers.get("Authorization", "")
        token = authorization_header.split("Bearer ")[1]
        user_info = is_authenticated(token)
        # checking create 'create-cluster' role is assign to the user.
        if user_info and "realm_access" in user_info:
            realm_roles = user_info["realm_access"]["roles"]
            if "create-cluster" not in realm_roles:
                # If the user does not have the 'create-cluster' role
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not allowed to create clusters",
                )
        print("token_verify :: ", user_info)
        response = {
            "status": status.HTTP_202_ACCEPTED,
            "realm_roles": user_info["realm_access"]["roles"],
            "user_id": user_info["sub"],
        }
        return generate_response(
            True, status.HTTP_202_ACCEPTED, "Token verified", [response]
        )
    except Exception as e:
        debug_response(e, "Error occurs on verifying token", "error")
        return generate_response(
            False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to verify token", []
        )


@router.post(
    "/subscription-request",
    response_description="request for subscription",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResponseModel,
)
def subscription_request(request: Request):
    """Request a subscription for the authenticated user."""
    try:
        authorization_header = request.headers.get("Authorization", "")
        token = authorization_header.split("Bearer ")[1]
        user_info = is_authenticated(token)
        user_id = user_info.get("sub")
        print("subscription_request :: ", user_id)
        status_code = None
        message = None

        user_groups = keycloak_admin.get_user_groups(user_id=user_info["sub"])

        if not user_groups:  # If user_groups is empty
            group_id = keycloak_admin.get_group_by_path(
                path="/" + REQUEST_GROUP_NAME
            ).get("id")
            keycloak_admin.group_user_add(user_id=user_id, group_id=group_id)
            status_code = status.HTTP_202_ACCEPTED
            message = "Subscription request sent successfully"
        elif any(group["name"] == REQUEST_GROUP_NAME for group in user_groups):
            return generate_response(
                False,
                status.HTTP_400_BAD_REQUEST,
                "User already requested for subscription",
                [],
            )
        else:
            return generate_response(
                False,
                status.HTTP_400_BAD_REQUEST,
                "User already approved for subscription",
                [],
            )

        response = {"status": status_code, "message": message}
        return generate_response(
            True,
            status.HTTP_202_ACCEPTED,
            "Subscription request sent successfully",
            [response],
        )
    except Exception as e:
        debug_response(e, "Error occurs on subscription request", "error")
        return generate_response(
            False,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to request subscription",
            [],
        )

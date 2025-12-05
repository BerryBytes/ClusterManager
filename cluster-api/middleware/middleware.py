"""Middleware for Keycloak authentication and user verification."""
import logging
import os

import jose
from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from keycloak import KeycloakOpenID
from pyparsing import Any
from schemas.user_schema import user_from_keycloak_dict, user_from_user_dict
from utills.common_response import debug_response, generate_response

# Check if REQUESTS_CA_BUNDLE environment variable exists
ca_bundle = os.getenv("REQUESTS_CA_BUNDLE")
if ca_bundle:
    os.environ["REQUESTS_CA_BUNDLE"] = ca_bundle
    print(f"REQUESTS_CA_BUNDLE is set to: {ca_bundle}")
else:
    print("Warning: REQUESTS_CA_BUNDLE environment variable is not set")

# Initialize KeycloakOpenID
try:
    keycloak_openid = KeycloakOpenID(
        server_url=os.getenv("KEYCLOAK_URL"),
        client_id=os.getenv("CLIENT_ID"),
        realm_name=os.getenv("REALM_NAME"),
        verify=True,
    )
except Exception as e:
    print(f"Error initializing KeycloakOpenID: {e}")

# List of public routes that do not require authentication
public_routes = [
    "/",
    "/public",
    "/v1/public/login",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
    "/v1/public/subscriptions",
    "/v1/public/cluster-status",
    "/v1/websocket/{user_id}",  # Fixed to match actual WebSocket endpoint with user_id parameter
]


# Middleware for Keycloak authentication
async def validate_keycloak_token(request: Request, call_next):
    # Check if the current route is public, if so, skip authentication
    """FastAPI middleware to validate Keycloak JWT token for protected routes.

    Args:
        request (Request): Incoming FastAPI request.
        call_next: Function to call the next middleware or route.

    Returns:
        Response: The response from the next handler if token is valid,
        or error response.
    """
    if request.url.path in public_routes:
        return await call_next(request)
    authorization_header = request.headers.get("Authorization", "")
    if not authorization_header or not authorization_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid Authorization header"},
        )
    token = authorization_header.split("Bearer ")[1]

    try:
        user_info = is_authenticated(token)
        check_user(user_info, request)
        return await call_next(request)
    except HTTPException as http_exception:
        raise http_exception
    except jose.exceptions.ExpiredSignatureError:
        return generate_response(
            False, status.HTTP_401_UNAUTHORIZED, "Token has expired", None
        )
    except jose.exceptions.JWTError:
        return generate_response(
            False, status.HTTP_401_UNAUTHORIZED, "Token is invalid", None
        )
    except Exception as e:
        debug_response(e, "Error occurs on validating token", "error")
        return generate_response(
            False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error", None
        )


def is_authenticated(credential: str):
    """Verify the JWT token using Keycloak public key.

    Args:
        credential (str): Bearer token from the request.

    Returns:
        dict: Decoded token payload if valid.

    Raises:
        ValueError: If the public key is invalid or token cannot be decoded.
    """
    token = credential
    try:
        # Verify the token and return the token claims if valid
        options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}

        # Ensure keycloak_public_key is valid
        keycloak_public_key = (
            "-----BEGIN PUBLIC KEY-----\n"
            + keycloak_openid.public_key()
            + "\n-----END PUBLIC KEY-----"
        )

        if not keycloak_public_key:
            raise ValueError("Keycloak public key is empty or invalid.")

        # Decode the token
        token_info = keycloak_openid.decode_token(
            token, key=keycloak_public_key, options=options
        )
        return token_info

    except ValueError as ve:
        debug_response(ve, "Error occurs on checking user", "error")
        raise
    except Exception as e:
        debug_response(e, "Error occurs on validating token", "error")
        raise


def check_user(userInfo: Any, request: Request):
    """Ensure the user exists in the database and attach it to request.state.user.

    Args:
        user_info (Any): Decoded token claims.
        request (Request): FastAPI request object with database access.

    Raises:
        Exception: If user processing or DB operations fail.
    """
    try:
        user = request.app.database["user"].find_one({"email": userInfo["email"]})
        user_obj = user_from_keycloak_dict(userInfo)
        if user is None:
            # User does not exist, insert the user into the database
            raw_user = jsonable_encoder(user_obj)
            request.app.database["user"].insert_one(raw_user)
        else:
            user_obj = user_from_user_dict(user)
        request.state.user = user_obj
    except Exception as e:
        debug_response(e, "Error occurs on checking user", "error")
        raise

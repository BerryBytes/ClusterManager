from fastapi.encoders import jsonable_encoder
from pyparsing import Any
import logging
from fastapi import Request, HTTPException,status
from fastapi.responses import JSONResponse
from keycloak import KeycloakOpenID
import jose
import os

from schemas.user_schema import user_from_keycloak_dict, user_from_user_dict
from utills.common_response import debug_response, generate_response

os.environ['REQUESTS_CA_BUNDLE'] = f"{os.getenv('REQUESTS_CA_BUNDLE')}"

# Initialize KeycloakOpenID
keycloak_openid = KeycloakOpenID(server_url=os.getenv('KEYCLOAK_URL'),
                                 client_id=os.getenv('CLIENT_ID'),
                                 realm_name=os.getenv('REALM_NAME'),
                                 verify=True
                                 )

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
    "/v1/public/cluster-status"
    "/v1/public/websocket",   
]


# Middleware for Keycloak authentication
async def validate_keycloak_token(request: Request, call_next):
    # Check if the current route is public, if so, skip authentication
    if request.url.path in public_routes:
        return await call_next(request)
    authorization_header = request.headers.get("Authorization", "")
    if not authorization_header or not authorization_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={'detail': "Missing or invalid Authorization header"})
    token = authorization_header.split("Bearer ")[1]

    try:
        user_info = is_authenticated(token)
        check_user(user_info, request)
        return await call_next(request)
    except HTTPException as http_exception:
        raise http_exception
    except jose.exceptions.ExpiredSignatureError:
        return generate_response(False, status.HTTP_401_UNAUTHORIZED, "Token has expired", None)
    except jose.exceptions.JWTError:
        return generate_response(False, status.HTTP_401_UNAUTHORIZED, "Token is invalid", None)
    except Exception as e:
        debug_response(e, "Error occurs on validating token", "error")
        return generate_response(False, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error", None)
    


def is_authenticated(credential: str):
    token = credential
    try:
        # Verify the token and return the token claims if valid
        options = {"verify_signature": True,
                   "verify_aud": False, "verify_exp": True}
        
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
    try:
        user = request.app.database["user"].find_one({"email": userInfo['email']})
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
    


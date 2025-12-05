"""
Subscription API Routes.

Provides endpoints to create, list, retrieve, and delete subscriptions.
"""

import os
from typing import List

from fastapi import APIRouter, Body, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from models.common_response import ResponseModel
from models.subscription import Subscription
from utills.common_response import debug_response, generate_response

router = APIRouter()


@router.post(
    "/",
    response_description="Create a new subscription",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseModel,
)
def create_subscription(request: Request, subscription: Subscription = Body(...)):
    """Create a new subscription in the database."""
    try:
        subscription = jsonable_encoder(subscription)
        new_subscription = request.app.database["subscription"].insert_one(subscription)
        created_subscription = request.app.database["subscription"].find_one(
            {"_id": new_subscription.inserted_id}
        )
        res = generate_response(
            True,
            status.HTTP_201_CREATED,
            "Subscription created successfully",
            created_subscription,
        )
        return res
    except Exception as e:
        debug_response(e)
        return generate_response(
            success=False,
            code=HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR),
            message="Failed to create subscription",
            data=None,
        )


@router.get(
    "", response_description="List all subscriptions", response_model=ResponseModel
)
def list_subscription(request: Request):
    """Retrieve a list of all subscriptions."""
    try:
        subscriptions = list(request.app.database["subscription"].find(limit=100))

        res = generate_response(
            success=True,
            code=status.HTTP_200_OK,
            message="List all subscriptions",
            data=subscriptions,
        )
        return res

    except Exception as e:
        debug_response(e)
        return generate_response(
            success=False,
            code=HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR),
            message="Failed to retrieve subscriptions",
            data={},
        )


@router.get(
    "/{id}",
    response_description="Get a single subscription by id",
    response_model=ResponseModel,
)
def find_subscription(id: str, request: Request):
    """Retrieve a subscription by its ID."""
    try:
        subscription = request.app.database["subscription"].find_one({"_id": id})
        if subscription is not None:
            return generate_response(
                True, status.HTTP_200_OK, "Subscription found", subscription
            )
        return generate_response(
            True, status.HTTP_204_NO_CONTENT, "Subscription not found", None
        )
    except Exception as e:
        debug_response(e)
        return generate_response(
            success=False,
            code=HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR),
            message="Failed to retrieve subscription",
            data=None,
        )


@router.delete(
    "/{id}",
    response_description="Delete a subscription",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ResponseModel,
)
def delete_subscription(id: str, request: Request):
    """Delete a subscription by its ID."""
    try:
        delete_result = request.app.database["subscription"].delete_one({"_id": id})
        if delete_result.deleted_count == 1:
            return generate_response(
                True,
                status.HTTP_204_NO_CONTENT,
                "Subscription deleted successfully",
                None,
            )
        return generate_response(
            True, status.HTTP_404_NOT_FOUND, "Subscription not found", None
        )
    except Exception as e:
        debug_response(e)
        return generate_response(
            success=False,
            code=HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR),
            message="Failed to delete subscription",
            data=None,
        )

"""
Module for creating User objects from different dictionary formats.

Provides utility functions to convert data from Keycloak or
internal user dicts to User model instances.
"""
from models.user import User
from pyparsing import Any


def user_from_keycloak_dict(res: Any):
    """Convert a Keycloak dictionary to a User object."""
    return User(
        id=res.get("sid", "2122fd0b-d673-41a9-a2d2-36133d5eaa78"),
        name=res.get("name", res.get("preferred_username", "user")),
        email=res.get("email", "a@b.com"),
        userName=res.get("preferred_username", "user"),
    )


def user_from_user_dict(res: Any):
    """Convert an internal user dictionary to a User object."""
    return User(
        id=res.get("_id", ""),
        name=res.get("name", res.get("userName", "user")),
        email=res.get("email", "a@b.com"),
        userName=res.get("userName", "user"),
    )

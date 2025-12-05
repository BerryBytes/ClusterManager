"""
Utility functions for cluster operations.

Includes serializers and validators for cluster data.
"""
import json
import re
from email.quoprimime import unquote
from pipes import quote


def clusters_serializer(res):
    """
    Serialize a cluster document into a standardized dictionary.

    Args:
        cluster (dict): Cluster document from the database.

    Returns:
        dict: Serialized cluster data.
    """
    response = {
        "id": res["_id"],
        "name": res["name"],
        "user_id": res["user_id"],
        "stauts": res["status"],
        "host_cluster_id": res["host_cluster_id"],
        "kube_version": res["kube_version"],
        "created": res["created"],
        "subscription_id": res["subscription_id"],
    }
    return response


def is_valid_url_name(name):
    """Check if a cluster name is valid for URLs."""
    if not name:
        return False, "Name cannot be empty."

    # Check if the name is too long
    if len(name) > 255:
        return False, "Name is too long"

    # Check if the name contains only valid characters (letters, digits, hyphens, and underscores)
    if not re.match(r"^[a-zA-Z0-9-_]+$", name):
        return (
            False,
            "Name contains invalid characters. Only letters, digits, hyphens, and underscores are allowed.",
        )

    return True, None

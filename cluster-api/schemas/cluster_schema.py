from email.quoprimime import unquote
import json
from pipes import quote
import re


def clusters_serializer(res):
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
    # Check if the name is empty
    if not name:
        return False, "Name cannot be empty."

    # Check if the name is too long
    if len(name) > 255:
        return False, "Name is too long"

    # Check if the name contains only valid characters (letters, digits, hyphens, and underscores)
    if not re.match(r'^[a-zA-Z0-9-_]+$', name):
        return False, "Name contains invalid characters. Only letters, digits, hyphens, and underscores are allowed."
    
    return True, None
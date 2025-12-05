"""Flask routes for cluster management service."""
import json
import logging

from flask import Blueprint, jsonify, request
from src.usecases.use_cases import (
    check_host_cluster_usecase,
    create_cluster_usecase,
    delete_vcluster_usecase,
    generate_kubeconfig_usecase,
    get_cluster_status_usecase,
    start_cluster_usecase,
    stop_vcluster_usecase,
)

# Define a Blueprint for routes
routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/dapr/subscribe", methods=["GET"])
def subscribe():
    """Return the list of subscriptions for Dapr."""
    subscriptions = [
        {
            "pubsubname": "messagebus",
            "topic": "cluster-create",
            "route": "create-cluster",
        },
        {
            "pubsubname": "messagebus",
            "topic": "cluster-start",
            "route": "start-cluster",
        },
        {"pubsubname": "messagebus", "topic": "cluster-stop", "route": "stop-cluster"},
        {
            "pubsubname": "messagebus",
            "topic": "cluster-delete",
            "route": "delete-cluster",
        },
        {
            "pubsubname": "messagebus",
            "topic": "cluster-plan-upgrade",
            "route": "update-cluster-plan",
        },
    ]
    logging.info("Dapr pub/sub is subscribed to: %s", json.dumps(subscriptions))
    return jsonify(subscriptions)


@routes_bp.route("/create-cluster", methods=["POST"])
def create_cluster():
    """Handle cluster creation."""
    return create_cluster_usecase(request.json)


@routes_bp.route("/cluster-check", methods=["POST"])
def check_host_cluster():
    """Check the status of a host cluster."""
    return check_host_cluster_usecase(request.json)


@routes_bp.route("/start-cluster", methods=["POST"])
def start_cluster():
    """Start a cluster."""
    return start_cluster_usecase(request.json)


@routes_bp.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"message": "Cluster service running"}), 200


@routes_bp.route("/host-cluster/cluster/status", methods=["POST"])
def get_cluster_status():
    """Get the status of a cluster."""
    return get_cluster_status_usecase(request.json)


@routes_bp.route("/stop-cluster", methods=["POST"])
def stop_vcluster():
    """Stop a virtual cluster."""
    return stop_vcluster_usecase(request.json)


@routes_bp.route("/delete-cluster", methods=["POST"])
def delete_cluster():
    """Delete a cluster."""
    return delete_vcluster_usecase(request.json)


@routes_bp.route("/generate-config", methods=["POST"])
def generate_config():
    """Generate a kubeconfig for a cluster."""
    return generate_kubeconfig_usecase(request.json)

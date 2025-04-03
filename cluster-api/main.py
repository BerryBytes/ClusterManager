import logging
import os
from fastapi import Depends, FastAPI
from fastapi.middleware import Middleware
from pymongo import MongoClient
from middleware.dependency import has_access
from middleware.middleware import validate_keycloak_token
from routes.host_cluster import router as host_cluster_router
from routes.subscription import router as subscription_route
from routes.kube_list import router as kube_route
from routes.public import router as public_route
from routes.user import router as user_route
from routes.cluster import router as cluster
from fastapi.middleware.cors import CORSMiddleware
from utills.seeder import seed_db
from routes.websocket import router as websocket_router

app = FastAPI()

app.middleware("http")(validate_keycloak_token)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# routes
PROTECTED = [Depends(has_access)]

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(os.getenv('ATLAS_URI'))
    app.database = app.mongodb_client[os.getenv('DB_NAME')]
    logging.basicConfig(level=logging.INFO)

    # Check if collections exist and seed data if they do not
    collections = ["hostCluster", "user", "subscription", "cluster", "kubeversion"]
    for collection in collections:
        if collection not in app.database.list_collection_names():
            logging.info(f"Collection {collection} not found. Seeding data...")
            seed_db(app.database)

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
app.include_router(public_route, tags=["public"], prefix="/v1/public")
app.include_router(host_cluster_router, tags=["host-cluster"], prefix="/v1/host-clusters", dependencies=PROTECTED)
app.include_router(subscription_route, tags=["subscription"], prefix="/v1/subscriptions", dependencies=PROTECTED)
app.include_router(kube_route, tags=["kubeversion"], prefix="/v1/kubeversion", dependencies=PROTECTED)
app.include_router(user_route, tags=["user"], prefix="/v1/users", dependencies=PROTECTED)
app.include_router(cluster, tags=["cluster"], prefix="/v1/clusters", dependencies=PROTECTED)
app.include_router(websocket_router, tags=["websocket"], prefix="/v1/websocket")

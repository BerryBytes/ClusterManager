"""
Seeder module to populate the database with initial test data.

This module seeds collections for host clusters, users, subscriptions,
clusters, and kube versions for development or testing purposes.
"""


def seed_db(db):
    """
    Seed the database with initial test data.

    Args:
        db: Database connection (e.g., MongoDB client) where collections
            will be seeded.
    """
    host_clusters = [
        {
            "_id": "4d17f7f0-752b-4a5e-844b-915a55876b22",
            "name": "cluster-1",
            "user_id": "da812999-c98a-445a-b759-bc7e21524d7c",
            "region": "us-east-1",
            "provider": "aws",
            "nodes": 1,
            "active": True,
            "version": "1.25",
            "created": "2022-01-01T00:00:00.000Z",
            "updated": "2022-01-01T00:00:00.000Z",
        },
        {
            "_id": "4d17f7f0-752b-4a5e-844b-915a55876b23",
            "name": "cluster-2",
            "user_id": "da812999-c98a-445a-b759-bc7e21524d7d",
            "region": "us-west-1",
            "provider": "aws",
            "nodes": 2,
            "active": True,
            "version": "1.26",
            "created": "2022-01-01T00:00:00.000Z",
            "updated": "2022-01-01T00:00:00.000Z",
        },
    ]
    db["hostCluster"].insert_many(host_clusters)

    # Seed user collection
    users = [
        {
            "_id": "da812999-c98a-445a-b759-bc7e21524d7c",
            "name": "umesh khatiwada",
            "email": "a@b.com",
            "userName": "user",
        },
        {
            "_id": "da812999-c98a-445a-b759-bc7e21524d7d",
            "name": "john doe",
            "email": "john@doe.com",
            "userName": "johndoe",
        },
    ]
    db["user"].insert_many(users)

    # Seed subscription collection
    subscriptions = [
        {
            "_id": "039623b9-c20e-4f0e-a81a-de85a550ef19",
            "name": "basic",
            "pods": 10,
            "service": 10,
            "configMap": 10,
            "persistanceVolClaims": 10,
            "replication_ctl": 10,
            "secrets": 10,
            "loadbalancer": 0,
            "nodePort": 10,
            "created": "2022-01-01T00:00:00.000Z",
            "updated": "2022-01-01T00:00:00.000Z",
        },
        {
            "_id": "039623b9-c20e-4f0e-a81a-de85a550ef20",
            "name": "premium",
            "pods": 20,
            "service": 20,
            "configMap": 20,
            "persistanceVolClaims": 20,
            "replication_ctl": 20,
            "secrets": 20,
            "loadbalancer": 1,
            "nodePort": 20,
            "created": "2022-01-01T00:00:00.000Z",
            "updated": "2022-01-01T00:00:00.000Z",
        },
    ]
    db["subscription"].insert_many(subscriptions)

    # Seed cluster collection
    clusters = [
        {
            "_id": "5a9539f2-668e-4e3d-9ae8-0823c8ae2ebb",
            "name": "test1",
            "user_id": "da812999-c98a-445a-b759-bc7e21524d7c",
            "status": "Stopped",
            "kube_version": "v1.30.0",
            "host_cluster_id": "4d17f7f0-752b-4a5e-844b-915a55876b22",
            "subscription_id": "039623b9-c20e-4f0e-a81a-de85a550ef19",
            "created": "2022-01-01T00:00:00.000Z",
            "updated": "2022-01-01T00:00:00.000Z",
        },
        {
            "_id": "5a9539f2-668e-4e3d-9ae8-0823c8ae2ebc",
            "name": "test2",
            "user_id": "da812999-c98a-445a-b759-bc7e21524d7d",
            "status": "Running",
            "kube_version": "v1.31.0",
            "host_cluster_id": "4d17f7f0-752b-4a5e-844b-915a55876b23",
            "subscription_id": "039623b9-c20e-4f0e-a81a-de85a550ef19",
            "created": "2022-01-01T00:00:00.000Z",
            "updated": "2022-01-01T00:00:00.000Z",
        },
    ]
    db["cluster"].insert_many(clusters)

    # Seed kubeversion collection
    kube_versions = [
        {
            "_id": "5a9539f2-668e-4e3d-9ae8-0823c8ae2ebd",
            "name": "v1.25.0",
            "active": True,
            "kube_version": "v1.25.0",
        },
        {
            "_id": "5a9539f2-668e-4e3d-9ae8-0823c8ae2ebe",
            "name": "v1.26,0",
            "active": True,
            "kube_version": "v1.26.0",
        },
    ]
    db["kubeversion"].insert_many(kube_versions)

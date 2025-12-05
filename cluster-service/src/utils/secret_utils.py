"""Utility functions for retrieving secrets from Dapr's Vault integration."""

import logging
from http.client import HTTPException

from dapr.clients import DaprClient


def get_vault_secret(secret_Id):
    """
    Retrieve a specific secret value from the Vault secret store via Dapr.

    Logs the request, fetches the secret from the Dapr secret store named
    "vault", and returns the value associated with the given secret_id.
    Raises an HTTPException if the retrieval fails.
    """
    logging.info("SCRET_ID :: %s", secret_Id)
    try:
        with DaprClient() as dprClient:
            secret = dprClient.get_secret(store_name="vault", key="dapr")
            secret = secret.secret.get(secret_Id)
            logging.info("Secret From VAult :: %s", secret)
            return secret
    except Exception as e:
        logging.error("Error on fetching secret :: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

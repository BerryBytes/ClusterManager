import logging
from dapr.clients import DaprClient
from http.client import HTTPException

def get_vault_secret(secret_Id):
    logging.info("SCRET_ID :: %s",secret_Id)
    try:
        with DaprClient() as dprClient:
            secret = dprClient.get_secret(store_name="vault", key="dapr")
            secret = secret.secret.get(secret_Id)        
            logging.info('Secret From VAult :: %s', secret)
            return secret
    except Exception as e:
            logging.error("Error on fetching secret :: %s", str(e))
            raise HTTPException(status_code=500, detail=str(e))  
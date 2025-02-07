import logging
import os
import re
from fastapi import HTTPException,status
import requests


def extract_time_components(time_string):
    pattern = r'(\d+)h(\d+)m|(\d+)h|(\d+)m'
    match = re.match(pattern, time_string)

    if match:
        hours = match.group(1) or match.group(3)
        minutes = match.group(2) or match.group(4)
        return  int(hours) * 3600  if hours is not None  else 0 + int(minutes) *60 if minutes is not None  else 0
        
    else:
        return None
    

def get_best_cluster(host_cluster_ids):
    payload = {
    "host_cluster_ids": host_cluster_ids
    }
    baseUrl = os.getenv('SERVICE_URL')
    response = requests.post(baseUrl+"/cluster-check", json=payload)
    if response.status_code == 200:  # Check if the request was successful
        print("POST request successful")
        responseBody = response.json()
        logging.info("response from select best cluster :: %s", str(responseBody))
        return responseBody["id"]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="resource not avialable in the current host")    
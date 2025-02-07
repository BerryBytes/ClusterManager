import logging
from jose import jwt
from jose.exceptions import JOSEError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

async def has_access(credentials: HTTPAuthorizationCredentials= Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, key='secret', options={"verify_signature": False,
                                                        "verify_aud": False,
                                                        "verify_iss": False})
        logging.info("Token payload :: %s",str(payload))
    except JOSEError as e:  # catches any exception
        raise HTTPException(
            status_code=401,    
            detail="Unauthorized")
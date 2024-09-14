from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import  Security, HTTPException
import os
# Define the expected API key and the header name
API_KEY = os.environ.get("API_KEY")
API_KEY_NAME = "api_key"

# Create an instance of APIKeyHeader, which will look for the key in the headers
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Dependency to validate the API key
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate API key"
        )
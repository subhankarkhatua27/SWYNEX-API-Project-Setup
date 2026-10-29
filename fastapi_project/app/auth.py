import os
import secrets
from pathlib import Path
from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials

# Ensure environment variables are loaded
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
load_dotenv()

EXPECTED_API_KEY = os.getenv("API_KEY", "swynex-secret-api-key-2026")

# Security schemes for OpenAPI / Swagger UI documentation
api_key_header_scheme = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API Key provided via 'X-API-Key' request header."
)

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="API Key provided as a Bearer token in 'Authorization: Bearer <key>'."
)


def verify_api_key(
    header_key: str | None = Security(api_key_header_scheme),
    bearer_creds: HTTPAuthorizationCredentials | None = Security(bearer_scheme)
) -> str:
    """
    Validates the incoming API key from either 'X-API-Key' header or
    'Authorization: Bearer <key>' header using constant-time comparison.
    Raises standard HTTPException with 401 status if missing or invalid.
    """
    provided_key: str | None = None

    if header_key:
        provided_key = header_key.strip()
    elif bearer_creds and bearer_creds.credentials:
        provided_key = bearer_creds.credentials.strip()

    if not provided_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid API key via the 'X-API-Key' header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    expected_key = os.getenv("API_KEY", EXPECTED_API_KEY)
    if not secrets.compare_digest(provided_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key provided. Access denied.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return provided_key

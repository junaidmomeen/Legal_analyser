import os
import time
import logging
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

logger = logging.getLogger(__name__)


ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        if os.getenv("APP_ENV", "development") == "production":
            raise ValueError("JWT_SECRET must be set in production environment")
        # Only allow insecure secret in development
        secret = "dev-insecure-secret"
        logger.warning("Using insecure JWT secret in development mode")
    elif len(secret) < 32:
        raise ValueError("JWT_SECRET must be at least 32 characters long")
    return secret


def create_token(subject: str, expires_in_seconds: int = 3600, claims: Optional[Dict[str, Any]] = None) -> str:
    to_encode = {"sub": subject, "exp": int(time.time()) + expires_in_seconds}
    if claims:
        to_encode.update(claims)
    return jwt.encode(to_encode, _get_secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, _get_secret(), algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e


async def require_auth(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    payload = decode_token(token)
    return payload


async def enforce_content_length_limit(request: Request) -> None:
    """Early guard: reject requests with Content-Length exceeding configured max size.
    Relies on client setting Content-Length; deeper checks still occur later.
    """
    max_mb = float(os.getenv("MAX_FILE_SIZE_MB", os.getenv("MAX_FILE_SIZE", "50")))
    max_bytes = int(max_mb * 1024 * 1024)
    content_length = request.headers.get("content-length")
    if content_length is None:
        return


def create_signed_url_token(resource_id: str, expires_in_seconds: int = 300) -> str:
    """Create a short-lived token for signed URL downloads."""
    return create_token(subject=f"resource:{resource_id}", expires_in_seconds=expires_in_seconds)


def verify_signed_url_token(token: str, resource_id: str) -> bool:
    try:
        payload = decode_token(token)
        return payload.get("sub") == f"resource:{resource_id}"
    except Exception:
        return False
    try:
        if int(content_length) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request too large. Max {max_mb:.0f}MB"
            )
    except ValueError:
        # Ignore invalid header; later validators will catch actual size
        return



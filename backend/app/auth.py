from __future__ import annotations

from typing import TypedDict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.config import Settings, get_settings

_bearer = HTTPBearer(auto_error=False)
_allowed_issuers = {"accounts.google.com", "https://accounts.google.com"}


class AuthenticatedUser(TypedDict):
    sub: str
    email: str
    name: str


def _allowed_email_set(raw_value: str) -> set[str]:
    return {item.strip().lower() for item in raw_value.split(",") if item.strip()}


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: Settings = Depends(get_settings),
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    token = credentials.credentials
    try:
        claims = google_id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.google_oauth_client_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {exc}",
        ) from exc

    issuer = str(claims.get("iss", ""))
    if issuer not in _allowed_issuers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer.",
        )

    if not claims.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified by Google.",
        )

    email = str(claims.get("email", "")).strip().lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not include an email claim.",
        )

    allowed_emails = _allowed_email_set(settings.allowed_emails)
    if not allowed_emails:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth is misconfigured: ALLOWED_EMAILS is empty.",
        )

    if email not in allowed_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated user is not authorized for this app.",
        )

    return {
        "sub": str(claims.get("sub", "")),
        "email": email,
        "name": str(claims.get("name", "")),
    }

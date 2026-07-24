import secrets

from fastapi import Header, HTTPException

from app.core.config import settings

_active_tokens: set[str] = set()  # in-memory: fine for a single-operator, single-process console


def issue_token(passphrase: str) -> str:
    if not secrets.compare_digest(passphrase, settings.dashboard_passphrase):
        raise HTTPException(status_code=401, detail="Incorrect passphrase")
    token = secrets.token_urlsafe(32)
    _active_tokens.add(token)
    return token


def require_auth(authorization: str = Header(default="")) -> None:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token not in _active_tokens:
        raise HTTPException(status_code=401, detail="Not authenticated")
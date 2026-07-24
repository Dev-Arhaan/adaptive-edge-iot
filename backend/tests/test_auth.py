# tests/test_auth.py
from fastapi import HTTPException

from app.core.auth import issue_token, require_auth

from fastapi.testclient import TestClient

from app.core.config import settings


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"passphrase": settings.dashboard_passphrase},
    )
    assert response.status_code == 200

    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}

def test_issue_token_rejects_wrong_passphrase():
    try:
        issue_token("definitely-wrong")
        assert False, "expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401


def test_require_auth_rejects_missing_header():
    try:
        require_auth(authorization="")
        assert False, "expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401
# tests/test_simulation_api.py
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def test_simulation_requires_auth():
    response = TestClient(app).get("/api/v1/simulation/state")
    assert response.status_code == 401


def test_login_then_start_and_fetch_nodes():
    client = TestClient(app)
    login = client.post("/api/v1/auth/login", json={"passphrase": settings.dashboard_passphrase})
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/simulation/start", json={"node_count": 10}, headers=headers)
    nodes = client.get("/api/v1/simulation/nodes", headers=headers)

    assert nodes.status_code == 200
    assert len(nodes.json()) == 10
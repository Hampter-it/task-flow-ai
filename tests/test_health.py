from fastapi.testclient import TestClient

from taskflow.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_json_content_type() -> None:
    response = client.get("/health")

    assert response.headers["content-type"].startswith("application/json")


def test_openapi_documents_health_check() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    operation = response.json()["paths"]["/health"]["get"]

    assert operation["operationId"] == "healthCheck"
    assert "200" in operation["responses"]

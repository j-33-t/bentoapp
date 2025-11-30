from fastapi.testclient import TestClient

from bentoapp.examples.demo.main import app


def test_root_renders():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "bentoapp" in resp.text.lower()

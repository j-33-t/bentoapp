from fastapi.testclient import TestClient

from bentoapp.examples.demo.main import app


def test_table_endpoint_renders():
    client = TestClient(app)
    resp = client.get("/_bento/table/demo-table")
    assert resp.status_code == 200
    assert "demo-table" in resp.text

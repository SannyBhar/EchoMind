def test_health_endpoint_returns_ok(api_client) -> None:
    response = api_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "timestamp_utc" in payload


def test_demo_memory_endpoint_returns_payload(api_client) -> None:
    response = api_client.get("/memory/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["memory_id"] == "demo-memory-001"

from scripts.seed_demo_data import seed_demo_data


def test_memories_endpoint_returns_seeded_data(api_client, db_session) -> None:
    seed_demo_data(db_session)
    db_session.commit()

    response = api_client.get("/memories")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["external_id"] == "demo-memory-001"
    assert len(payload[0]["people"]) == 2


def test_memory_detail_endpoint_returns_seeded_memory(api_client, db_session) -> None:
    seed_demo_data(db_session)
    db_session.commit()

    list_response = api_client.get("/memories")
    memory_id = list_response.json()[0]["id"]

    response = api_client.get(f"/memories/{memory_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["external_id"] == "demo-memory-001"
    assert payload["place"]["name"] == "New Brunswick Campus"

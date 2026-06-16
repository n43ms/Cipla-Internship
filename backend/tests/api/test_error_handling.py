from backend.app.utils.errors import error_payload


def test_health_route(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_error_payload_shape() -> None:
    payload = error_payload("bad_filter", "Invalid filter", "country")

    assert payload == {
        "error": {
            "code": "bad_filter",
            "message": "Invalid filter",
            "field": "country",
            "context": {},
        }
    }

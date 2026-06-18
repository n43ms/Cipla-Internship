from backend.app.utils.errors import error_payload


def test_health_route(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_local_vite_origins_are_allowed_for_cors(client) -> None:
    response = client.options(
        "/api/execution/summary",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


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

from fastapi.testclient import TestClient

from app.main import app, limiter

client = TestClient(app)


def test_ready_is_503_until_vector_db_is_built(monkeypatch):
    import app.services.similarity as sim

    monkeypatch.setattr(sim, "_VECTOR_DB_INITIALIZED", False)
    response = client.get("/ready")
    assert response.status_code == 503
    assert "vector_db" in response.json()["detail"]["problems"]


def test_ready_when_everything_is_loaded(monkeypatch):
    import app.services.similarity as sim

    monkeypatch.setattr(sim, "_VECTOR_DB_INITIALIZED", True)
    monkeypatch.setattr(sim, "VECTOR_DB", {1: "player"})
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["vector_db_size"] == 1


def test_visualizations_are_cached_by_clients(monkeypatch):
    import app.services.visualizations as viz

    monkeypatch.setattr(viz, "player_heatmap", lambda player_id, match_id: b"\x89PNG\r\n\x1a\n")
    response = client.get("/api/v1/viz/player/20485/heatmap?match_id=3890563")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert "max-age=86400" in response.headers["cache-control"]

    monkeypatch.setattr(viz, "player_heatmap", lambda player_id, match_id: None)
    missing = client.get("/api/v1/viz/player/20485/heatmap?match_id=3890563")
    assert missing.status_code == 404
    assert "cache-control" not in missing.headers


def test_rate_limit_returns_429():
    try:
        codes = {client.get("/health").status_code for _ in range(125)}
    finally:
        limiter.reset()
    assert 429 in codes

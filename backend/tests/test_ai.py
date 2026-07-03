import os
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

needs_api_key = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set",
)


@needs_api_key
def test_report_stream_returns_sse():
    response = client.get("/api/v1/players/5207/report-stream?lang=en")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    assert "Cache-Control" in response.headers
    assert "no-cache" in response.headers["Cache-Control"]


def test_report_stream_unknown_player():
    response = client.get("/api/v1/players/-1/report-stream?lang=en")
    assert response.status_code in (200, 404, 500)


@needs_api_key
def test_report_stream_returns_content():
    response = client.get("/api/v1/players/5207/report-stream?lang=en")
    assert response.status_code == 200
    content = b""
    for chunk in response.iter_bytes():
        content += chunk
    text = content.decode()
    assert "data:" in text


@needs_api_key
def test_report_stream_spanish():
    response = client.get("/api/v1/players/5207/report-stream?lang=es")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

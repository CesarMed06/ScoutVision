"""Tests for the advanced scout filters."""

import pytest
from fastapi.testclient import TestClient

import app.services.similarity as sim
from app.main import app
from app.services.scout import scout_players


def _player(name, goals, minutes=900):
    return {
        "name": name,
        "player_info": {"team": "T", "competition": "C"},
        "totals": {"minutes": minutes, "goals": goals, "xg": 0, "xa": 0},
    }


@pytest.fixture
def fake_db(monkeypatch):
    db = {
        1: _player("Alpha", 9),
        2: _player("Bravo", 9),
        3: _player("Charlie", 3, minutes=0),
    }
    monkeypatch.setattr(sim, "VECTOR_DB", db)
    return db


def test_sort_by_metric_with_stable_tiebreak(fake_db):
    rows = scout_players(sort_by="goals_per_90", sort_dir="desc")

    assert [r["player_name"] for r in rows] == ["Alpha", "Bravo", "Charlie"]


def test_sort_direction_asc(fake_db):
    rows = scout_players(sort_by="goals_per_90", sort_dir="asc")

    assert rows[0]["player_name"] == "Charlie"
    assert rows[-1]["goals_per_90"] == 0.9


def test_zero_minutes_are_not_reported_as_one_minute(fake_db):
    rows = scout_players(sort_by="goals_per_90", sort_dir="asc")
    charlie = next(r for r in rows if r["player_name"] == "Charlie")

    assert charlie["minutes"] == 0
    assert charlie["goals_per_90"] == 0


def test_filters_apply_before_limit(fake_db):
    rows = scout_players(min_goals_per_90=0.5, limit=1)

    assert len(rows) == 1
    assert rows[0]["player_name"] == "Alpha"


def test_unknown_sort_by_is_rejected():
    client = TestClient(app)

    res = client.get("/api/v1/players/search/advanced", params={"sort_by": "nope"})

    assert res.status_code == 422


def test_valid_sort_by_is_accepted(fake_db):
    client = TestClient(app)

    res = client.get("/api/v1/players/search/advanced", params={"sort_by": "pass_pct", "sort_dir": "asc"})

    assert res.status_code == 200
    assert len(res.json()) == 3

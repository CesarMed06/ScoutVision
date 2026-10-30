"""Test for search_players."""

import json

import pandas as pd


def test_search_players_returns_list():
    """Test that search_players returns a non-empty DataFrame."""
    from app.services.statsbomb import search_players

    df = search_players(limit=100)
    assert df is not None
    assert len(df) > 0, "Expected at least one player in the index"
    required_cols = {"player_id", "player_name", "team", "match_id", "competition"}
    assert required_cols.issubset(df.columns), f"Missing columns: {required_cols - set(df.columns)}"
    assert df["player_id"].nunique() > 0, "Expected at least one unique player"


def test_search_players_filter():
    """Test that search_players filters by query."""
    from app.services.statsbomb import search_players

    df = search_players(query="Ronaldo", limit=100)
    assert len(df) > 0, "Expected at least one Ronaldo"
    assert all("ronaldo" in name.lower() for name in df["player_name"]), "All results should contain 'Ronaldo'"


def test_search_players_limit():
    """Test that search_players respects the limit parameter."""
    from app.services.statsbomb import search_players

    df = search_players(limit=5)
    assert len(df) <= 5, f"Expected at most 5 players, got {len(df)}"


def test_search_players_normalizes_diacritics_and_deduplicates(monkeypatch):
    from app.services import statsbomb

    players = pd.DataFrame([
        {"player_id": 1, "player_name": "João Félix", "match_id": 10},
        {"player_id": 1, "player_name": "João Félix", "match_id": 11},
        {"player_id": 2, "player_name": "Joao Felix", "match_id": 12},
        {"player_id": 3, "player_name": "Other Player", "match_id": 13},
    ])
    monkeypatch.setattr(statsbomb, "_load_cached", lambda _: None)
    monkeypatch.setattr(statsbomb, "_build_player_index", lambda: players)

    result = statsbomb.search_players(query=" joao felix ", limit=2)

    assert result["player_id"].tolist() == [1, 2]
    assert result["match_id"].tolist() == [10, 12]


def test_search_players_escapes_query_metacharacters(monkeypatch):
    from app.services import statsbomb

    players = pd.DataFrame([
        {"player_id": 1, "player_name": "A+B Player"},
        {"player_id": 2, "player_name": "AAAB Player"},
    ])
    monkeypatch.setattr(statsbomb, "_load_cached", lambda _: None)
    monkeypatch.setattr(statsbomb, "_build_player_index", lambda: players)

    result = statsbomb.search_players(query="A+B")

    assert result["player_id"].tolist() == [1]


def test_demo_mode_returns_cached_player_photo(monkeypatch, tmp_path):
    from app.services import player_images

    monkeypatch.setattr(player_images, "CACHE_FILE", tmp_path / "photos.json")
    monkeypatch.setattr(player_images.settings, "demo_mode", True)
    player_images.CACHE_FILE.write_text(json.dumps({"Bernd Leno": {"thumb": "https://example.com/leno.jpg"}}))

    assert player_images.get_player_image("Bernd Leno") == "https://example.com/leno.jpg"
    assert player_images.get_player_image("Unknown Player") is None


def test_photo_cache_saves_merge_concurrent_entries(monkeypatch, tmp_path):
    from app.services import player_images

    monkeypatch.setattr(player_images, "CACHE_FILE", tmp_path / "photos.json")
    monkeypatch.setattr(player_images.settings, "demo_mode", False)
    player_images._save_cache({"Bernd Leno": {"thumb": "https://example.com/leno.jpg"}})
    player_images._save_cache({"Julian Brandt": {"thumb": "https://example.com/brandt.jpg"}})

    cache = json.loads(player_images.CACHE_FILE.read_text())
    assert set(cache) == {"Bernd Leno", "Julian Brandt"}

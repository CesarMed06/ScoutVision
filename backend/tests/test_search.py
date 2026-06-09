"""Test for search_players."""


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

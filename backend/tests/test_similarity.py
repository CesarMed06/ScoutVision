"""Tests for player similarity."""


def test_similarity_returns_sorted_results():
    """Test that get_similar_players returns sorted results."""
    from app.services.similarity import init_vector_db

    # Ensure vector DB is initialized
    init_vector_db(max_players=50)

    from app.services.similarity import get_similar_players

    # Use a known player_id from our data (Cristiano Ronaldo)
    results = get_similar_players(5207, top_n=5)
    assert results is not None
    assert len(results) > 0, "Expected at least one similar player"
    assert len(results) <= 5, f"Expected at most 5 results, got {len(results)}"

    # Check required keys
    for r in results:
        assert "player_id" in r, "Missing player_id"
        assert "player_name" in r, "Missing player_name"
        assert "similarity" in r, "Missing similarity"
        assert 0 <= r["similarity"] <= 1, f"Similarity should be between 0 and 1, got {r['similarity']}"

    # Check sorted descending
    sims = [r["similarity"] for r in results]
    assert sims == sorted(sims, reverse=True), "Results should be sorted by similarity descending"
    assert results[0]["player_id"] != 5207, "Should not include the target player"


def test_similarity_unknown_player():
    """Test that similarity returns empty list for unknown player."""
    from app.services.similarity import get_similar_players

    results = get_similar_players(-1)
    assert results == [], "Expected empty list for unknown player"


def _totals(minutes, **extra):
    base = {
        "minutes": minutes,
        "goals": 0,
        "xg": 0.0,
        "xa": 0,
        "key_passes": 0,
        "dribbles": 0,
        "tackles": 0,
        "passes": 0,
        "passes_completed": 0,
        "aerial_duels": 0,
        "aerial_duels_won": 0,
    }
    base.update(extra)
    return base


def test_global_averages_ignore_short_cameos(monkeypatch):
    from app.services import similarity

    monkeypatch.setattr(similarity, "VECTOR_DB", {
        1: {"totals": _totals(900, goals=9, passes=100, passes_completed=80,
                              aerial_duels=10, aerial_duels_won=4)},
        2: {"totals": _totals(10, goals=5, passes=100, passes_completed=0)},
    })
    monkeypatch.setattr(similarity, "_VECTOR_DB_INITIALIZED", True)

    avgs = similarity.get_global_averages()
    assert avgs["players_sampled"] == 1
    assert avgs["goals_per_90"] == 0.9
    assert avgs["pass_completion_pct"] == 80.0
    assert avgs["aerial_success_pct"] == 40.0


def test_global_averages_leave_percentages_empty_without_attempts(monkeypatch):
    from app.services import similarity

    monkeypatch.setattr(similarity, "VECTOR_DB", {
        1: {"totals": _totals(300, passes=50, passes_completed=25)},
    })
    monkeypatch.setattr(similarity, "_VECTOR_DB_INITIALIZED", True)

    avgs = similarity.get_global_averages()
    assert avgs["players_sampled"] == 1
    assert avgs["pass_completion_pct"] == 50.0
    assert avgs["aerial_success_pct"] is None


def test_global_averages_unavailable_while_index_builds(monkeypatch):
    from app.services import similarity

    monkeypatch.setattr(similarity, "_VECTOR_DB_INITIALIZED", False)
    assert similarity.get_global_averages() == {"players_sampled": 0}


def test_similarity_skips_players_without_enough_minutes(monkeypatch):
    from app.services import similarity

    similarity.init_vector_db(max_players=50)
    db = dict(similarity.VECTOR_DB)
    db[999999] = {
        "vector": [1.0] * len(similarity.METRIC_KEYS),
        "name": "Cameo",
        "totals": _totals(5, goals=3),
        "player_info": {"player_id": 999999, "player_name": "Cameo", "position": "Forward"},
    }
    monkeypatch.setattr(similarity, "VECTOR_DB", db)

    ids = [r["player_id"] for r in similarity.get_similar_players(5207, top_n=50)]
    assert 999999 not in ids

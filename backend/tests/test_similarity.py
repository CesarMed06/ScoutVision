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

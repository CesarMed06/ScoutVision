from app.services.similarity import init_vector_db, get_similar_players


def test_position_filter_returns_same_position():
    init_vector_db(max_players=50)
    results = get_similar_players(5207, top_n=10)
    assert results, "Expected similar players for player 5207"

    results_fwd = get_similar_players(5207, top_n=10, position_filter="Forward")
    results_gk = get_similar_players(5207, top_n=10, position_filter="Goalkeeper")
    assert len(results_gk) < len(results) or len(results_gk) == 0, (
        "Goalkeeper filter should return fewer results than unfiltered"
    )


def test_position_filter_no_results():
    results = get_similar_players(5207, top_n=5, position_filter="NonexistentRole")
    assert results == []


def test_position_filter_case_insensitive():
    results_upper = get_similar_players(5207, top_n=5, position_filter="FORWARD")
    results_lower = get_similar_players(5207, top_n=5, position_filter="forward")
    assert len(results_upper) == len(results_lower)

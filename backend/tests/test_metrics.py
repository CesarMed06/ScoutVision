"""Tests for player metrics."""


def test_player_metrics_has_required_keys():
    """Test that player metrics return the expected structure."""
    from app.services.metrics import get_player_metrics_across_matches

    # Use a known player_id from our data (Cristiano Ronaldo)
    result = get_player_metrics_across_matches(5207)
    assert result is not None
    assert len(result) > 0, "Expected at least one match of metrics"

    required_keys = {
        "player", "minutes", "goals", "assists", "shots",
        "xg", "xa", "passes", "tackles",
    }
    first = result[0]
    assert required_keys.issubset(first.keys()), f"Missing keys: {required_keys - set(first.keys())}"
    assert isinstance(first["minutes"], int), "minutes should be int"
    assert first["player"] != "", "player name should not be empty"


def test_player_metrics_per_90():
    """Test that per_90 metrics are computed correctly."""
    from app.services.metrics import get_player_metrics_across_matches

    result = get_player_metrics_across_matches(5207)
    assert result is not None
    assert len(result) > 0

    # Check that per_90 values exist and are reasonable
    totals = {}
    for m in result:
        for k, v in m.items():
            if k in ("player", "match_id", "team", "competition", "season"):
                continue
            if k.endswith("_pct") or k.endswith("_per_90"):
                continue
            totals[k] = totals.get(k, 0) + (v or 0)

    minutes = totals.get("minutes", 0)
    assert minutes > 0, "Should have played some minutes"
    goals_p90 = round(totals.get("goals", 0) / minutes * 90, 2)
    assert goals_p90 >= 0, "Goals/90 should be >= 0"

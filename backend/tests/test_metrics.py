"""Tests for player metrics."""


import pandas as pd


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


def _event(event_type, player=None, **values):
    return {"type": event_type, "player": player, **values}


def test_minutes_use_lineup_substitutions_and_full_time():
    from app.services.metrics import _infer_minutes

    events = pd.DataFrame([
        _event("Starting XI", tactics={"lineup": [{"player": {"name": "Starter"}}]}),
        _event("Starting XI", tactics={"lineup": [{"player": {"name": "Bench"}}]}),
        _event("Half End", period=1, minute=45, second=0),
        _event("Substitution", player="Starter", substitution_replacement="Sub", period=2, minute=60, second=30),
        _event("Substitution", player="Bench", substitution_replacement="SubbedOn", period=2, minute=55, second=30),
        _event("Half End", period=2, minute=90, second=0),
        _event("Pass", player="Starter", period=1, minute=10, second=0),
        _event("Pass", player="Sub", period=2, minute=70, second=0),
        _event("Pass", player="SubbedOn", period=2, minute=65, second=0),
    ])

    assert _infer_minutes(events, "Starter") == 61
    assert _infer_minutes(events, "Sub") == 30
    assert _infer_minutes(events, "SubbedOn") == 35


def test_shots_on_target_excludes_post_and_assists_need_goal_link():
    from app.services.metrics import compute_player_metrics

    events = pd.DataFrame([
        _event("Starting XI", tactics={"lineup": [{"player": {"name": "Forward"}}]}),
        _event("Half End", period=1, minute=45, second=0),
        _event("Half End", period=2, minute=90, second=0),
        _event("Shot", "Forward", minute=10, second=0, period=1, id="goal", shot_outcome="Goal", shot_statsbomb_xg=0.4),
        _event("Shot", "Forward", minute=20, second=0, period=1, id="post", shot_outcome="Post", shot_statsbomb_xg=0.2),
        _event("Shot", "Forward", minute=30, second=0, period=1, id="saved", shot_outcome="Saved", shot_statsbomb_xg=0.1),
        _event("Pass", "Forward", minute=9, second=50, period=1, pass_goal_assist=True, pass_shot_assist=True, pass_assisted_shot_id="goal"),
        _event("Pass", "Forward", minute=19, second=50, period=1, pass_goal_assist=True, pass_shot_assist=True, pass_assisted_shot_id="post"),
        _event("Pass", "Forward", minute=29, second=50, period=1, pass_goal_assist=True, pass_shot_assist=True, pass_assisted_shot_id="missing"),
    ])

    result = compute_player_metrics(events, "Forward")
    assert result["minutes"] == 90
    assert result["shots"] == 3
    assert result["shots_on_target"] == 2
    assert result["assists"] == 1
    assert result["key_passes"] == 3


def test_demo_match_metrics_match_statsbomb_events():
    import json
    from pathlib import Path

    from app.services.metrics import compute_player_metrics

    events_path = Path(__file__).resolve().parents[1] / "sample_data" / "events_3825833.json"
    events = pd.DataFrame(json.loads(events_path.read_text(encoding="utf-8")))
    metrics = compute_player_metrics(events, "Cristiano Ronaldo dos Santos Aveiro")

    assert metrics["minutes"] == 92
    assert metrics["shots"] == 8
    assert metrics["shots_on_target"] == 2
    assert metrics["assists"] == 0
    assert metrics["progressive_passes"] == 3


def test_progressive_passes_count_only_completed_threshold_advancing_passes():
    from app.services.metrics import compute_player_metrics

    events = pd.DataFrame([
        _event("Starting XI", tactics={"lineup": [{"player": {"name": "Midfielder"}}]}),
        _event("Half End", period=1, minute=45, second=0),
        _event("Half End", period=2, minute=90, second=0),
        _event("Pass", "Midfielder", minute=10, second=0, period=1, pass_outcome=None, location=[20, 30], pass_end_location=[50, 30]),
        _event("Pass", "Midfielder", minute=11, second=0, period=1, pass_outcome=None, location=[20, 30], pass_end_location=[49, 30]),
        _event("Pass", "Midfielder", minute=11, second=30, period=1, pass_outcome=None, location=[20, 30], pass_end_location=[60, 30]),
        _event("Pass", "Midfielder", minute=12, second=0, period=1, pass_outcome=None, location=[50, 30], pass_end_location=[65, 30]),
        _event("Pass", "Midfielder", minute=13, second=0, period=1, pass_outcome=None, location=[70, 30], pass_end_location=[80, 30]),
        _event("Pass", "Midfielder", minute=14, second=0, period=1, pass_outcome="Incomplete", location=[20, 30], pass_end_location=[60, 30]),
        _event("Pass", "Midfielder", minute=15, second=0, period=1, pass_outcome=None, location=[40, 30], pass_end_location=[30, 30]),
    ])

    result = compute_player_metrics(events, "Midfielder")
    assert result["progressive_passes"] == 4


def test_percentage_helper_distinguishes_zero_from_no_attempts():
    from app.services.metrics import percentage

    assert percentage(0, 0) is None
    assert percentage(5, 0) is None
    assert percentage(0, 4) == 0.0
    assert percentage(1, 4) == 25.0


def test_percentages_are_none_when_player_had_no_attempts():
    from app.services.metrics import compute_player_metrics

    events = pd.DataFrame([
        _event("Starting XI", tactics={"lineup": [{"player": {"name": "Keeper"}}]}),
        _event("Half End", period=1, minute=45, second=0),
        _event("Half End", period=2, minute=90, second=0),
        _event("Pass", "Keeper", minute=5, second=0, period=1, pass_outcome=None),
        _event("Pass", "Keeper", minute=15, second=0, period=1, pass_outcome=None),
        _event("Pressure", "Keeper", minute=20, second=0, period=1),
    ])

    result = compute_player_metrics(events, "Keeper")
    assert result["minutes"] == 90
    assert result["pass_completion_pct"] == 100.0
    # No attempts at all: the rate must be missing, never a fake 0%.
    assert result["dribble_success_pct"] is None
    assert result["duel_success_pct"] is None
    assert result["tackle_success_pct"] is None
    assert result["aerial_success_pct"] is None
    assert result["shot_accuracy"] is None
    assert result["passes_into_final_third_pct"] is None


def test_percentage_is_zero_when_attempts_were_made_but_none_completed():
    from app.services.metrics import compute_player_metrics

    events = pd.DataFrame([
        _event("Starting XI", tactics={"lineup": [{"player": {"name": "Winger"}}]}),
        _event("Half End", period=1, minute=45, second=0),
        _event("Half End", period=2, minute=90, second=0),
        _event("Pass", "Winger", minute=5, second=0, period=1, pass_outcome="Incomplete", location=[20, 30], pass_end_location=[85, 30]),
        _event("Dribble", "Winger", minute=10, second=0, period=1, dribble_outcome="Incomplete"),
        _event("Dribble", "Winger", minute=12, second=0, period=1, dribble_outcome="Incomplete"),
    ])

    result = compute_player_metrics(events, "Winger")
    assert result["pass_completion_pct"] == 0.0
    assert result["dribble_success_pct"] == 0.0
    assert result["passes_into_final_third"] == 1
    assert result["passes_into_final_third_completed"] == 0
    assert result["passes_into_final_third_pct"] == 0.0


def test_passes_into_final_third_split_attempted_and_completed():
    from app.services.metrics import compute_player_metrics

    events = pd.DataFrame([
        _event("Starting XI", tactics={"lineup": [{"player": {"name": "Playmaker"}}]}),
        _event("Half End", period=1, minute=45, second=0),
        _event("Half End", period=2, minute=90, second=0),
        # Completed, ends inside the final third.
        _event("Pass", "Playmaker", minute=10, second=0, period=1, pass_outcome=None, location=[60, 30], pass_end_location=[85, 30]),
        # Failed, also aimed into the final third: attempted but not completed.
        _event("Pass", "Playmaker", minute=11, second=0, period=1, pass_outcome="Incomplete", location=[60, 30], pass_end_location=[88, 30]),
        # Completed, but ends before the final third.
        _event("Pass", "Playmaker", minute=12, second=0, period=1, pass_outcome=None, location=[30, 30], pass_end_location=[70, 30]),
    ])

    result = compute_player_metrics(events, "Playmaker")
    assert result["passes_into_final_third"] == 2
    assert result["passes_into_final_third_completed"] == 1
    assert result["passes_into_final_third_pct"] == 50.0


def test_player_without_minutes_has_no_metrics():
    from app.services.metrics import _infer_minutes, compute_player_metrics

    events = pd.DataFrame([
        _event("Starting XI", tactics={"lineup": [{"player": {"name": "Starter"}}]}),
        _event("Half End", period=1, minute=45, second=0),
        _event("Half End", period=2, minute=90, second=0),
        _event("Substitution", player="Starter", substitution_replacement="Cameo", period=2, minute=90, second=0),
        _event("Pass", "Cameo", minute=90, second=0, period=2, pass_outcome=None),
    ])

    assert _infer_minutes(events, "Cameo") == 0
    assert compute_player_metrics(events, "Cameo") == {}
    assert compute_player_metrics(events, "Nobody") == {}


def test_normalize_pct_fields_clears_rates_without_attempts():
    from app.services.metrics import _normalize_pct_fields

    row = {
        "shots": 0,
        "shot_accuracy": 0,
        "dribbles": 3,
        "dribble_success_pct": 0.0,
        "aerial_duels": 0,
        "aerial_success_pct": 0.0,
    }

    _normalize_pct_fields(row)
    assert row["shot_accuracy"] is None
    assert row["aerial_success_pct"] is None
    # Attempts existed, so a real 0% survives.
    assert row["dribble_success_pct"] == 0.0


def test_aggregate_totals_does_not_divide_by_zero():
    from app.api.v1.metrics import _aggregate_totals

    matches = [
        {
            "player": "Test",
            "match_id": 1,
            "team": "Team",
            "competition": "League",
            "season": "2020",
            "minutes": 90,
            "goals": 0,
            "xg": 0.0,
            "xa": 0,
            "shots": 0,
            "shots_on_target": 0,
            "passes": 10,
            "passes_completed": 8,
            "dribbles": 0,
            "dribbles_completed": 0,
            "duels": 0,
            "duels_won": 0,
            "tackles": 0,
            "tackles_won": 0,
            "aerial_duels": 0,
            "aerial_duels_won": 0,
            "pressures": 2,
            "passes_into_final_third": 4,
            "passes_into_final_third_completed": 3,
        }
    ]

    totals = _aggregate_totals(matches)
    assert totals["pass_completion_pct"] == 80.0
    assert totals["passes_into_final_third_completed"] == 3
    assert totals["passes_into_final_third_pct"] == 75.0
    assert totals["shot_accuracy"] is None
    assert totals["dribble_success_pct"] is None
    assert totals["duel_success_pct"] is None
    assert totals["tackle_success_pct"] is None
    assert totals["aerial_success_pct"] is None


def test_aggregate_totals_skips_final_third_rate_for_legacy_rows():
    from app.api.v1.metrics import _aggregate_totals

    legacy = [
        {
            "player": "Legacy",
            "match_id": 1,
            "team": "Team",
            "competition": "League",
            "season": "2020",
            "minutes": 90,
            "passes": 5,
            "passes_completed": 4,
            "passes_into_final_third": 3,
        }
    ]

    totals = _aggregate_totals(legacy)
    assert "passes_into_final_third_pct" not in totals
    assert totals["pass_completion_pct"] == 80.0

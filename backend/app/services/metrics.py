import json
from functools import lru_cache

import pandas as pd

from app.core.config import settings
from app.services.statsbomb import DATA_DIR, SAMPLE_DATA_DIR, get_match_events, search_players

METRICS_DIR = DATA_DIR

FINAL_THIRD_X = 80
MIN_PROGRESSIVE_DIST = 10

AERIAL_WON_FLAGS = ("pass_aerial_won", "clearance_aerial_won", "shot_aerial_won")

PCT_ATTEMPT_SOURCES: dict[str, str] = {
    "shot_accuracy": "shots",
    "pass_completion_pct": "passes",
    "dribble_success_pct": "dribbles",
    "duel_success_pct": "duels",
    "tackle_success_pct": "tackles",
    "aerial_success_pct": "aerial_duels",
    "passes_into_final_third_pct": "passes_into_final_third",
}


def percentage(numerator: float, denominator: float, digits: int = 1) -> float | None:
    if not denominator:
        return None
    return round(numerator / denominator * 100, digits)


def _normalize_pct_fields(row: dict) -> dict:
    for pct_key, attempts_key in PCT_ATTEMPT_SOURCES.items():
        if pct_key in row and not row.get(attempts_key):
            row[pct_key] = None
    return row


def _event_minute(event: pd.Series) -> float | None:
    minute = event.get("minute")
    if pd.isna(minute):
        return None
    second = event.get("second", 0)
    second = 0 if pd.isna(second) else float(second)
    return float(minute) + second / 60


def _event_sort_key(event: pd.Series) -> tuple[float, float]:
    minute = event.get("minute")
    second = event.get("second", 0)
    return (
        float(minute) if pd.notna(minute) else 0.0,
        float(second) if pd.notna(second) else 0.0,
    )


def _is_in_starting_xi(events: pd.DataFrame, player: str) -> bool:
    starting_xi = events[events["type"] == "Starting XI"]
    for tactics in _col(starting_xi, "tactics"):
        if not isinstance(tactics, dict):
            continue
        for entry in tactics.get("lineup", []):
            if entry.get("player", {}).get("name") == player:
                return True
    return False


def _infer_minutes(events: pd.DataFrame, player: str) -> float:
    subs = events[events["type"] == "Substitution"]
    subbed_on = subs[_col(subs, "substitution_replacement").eq(player)]
    subbed_off = subs[_col(subs, "player").eq(player)]
    player_events = events[events["player"] == player]
    if player_events.empty:
        return 0

    half_ends = events[events["type"] == "Half End"]
    if not half_ends.empty and "period" in half_ends.columns:
        final_period = half_ends["period"].max()
        end_events = half_ends[half_ends["period"] == final_period]
    else:
        end_events = half_ends
    end_times = [
        value for value in (_event_minute(row) for _, row in end_events.iterrows())
        if value is not None
    ]
    if not end_times:
        end_times = [
            value for value in (_event_minute(row) for _, row in events.iterrows())
            if value is not None
        ]
    full_time = max(90.0, max(end_times, default=90.0))

    is_starter = _is_in_starting_xi(events, player)
    if not subbed_on.empty:
        sub_event = min(
            (row for _, row in subbed_on.iterrows()), key=_event_sort_key
        )
        start_min = _event_minute(sub_event)
    elif is_starter or not subbed_off.empty or player_events["minute"].le(1).any():
        start_min = 0.0
    else:
        event_minutes = [
            value
            for value in (_event_minute(row) for _, row in player_events.iterrows())
            if value is not None
        ]
        start_min = min(event_minutes, default=0.0)

    if not subbed_off.empty:
        sub_event = min(
            (row for _, row in subbed_off.iterrows()), key=_event_sort_key
        )
        end_min = _event_minute(sub_event)
    else:
        end_min = full_time
    if start_min is None or end_min is None:
        return 0
    return max(0, int(end_min - start_min + 0.5))


def _col(df, name):
    return df[name] if name in df.columns else pd.Series(index=df.index, dtype=float)


def _resolve_player(
    events: pd.DataFrame, player: str | None, player_id: int | None = None
) -> str | None:
    if player_id is not None and "player_id" in events.columns:
        rows = events[events["player_id"] == player_id]
        if len(rows) > 0:
            return rows["player"].iloc[0]
    return player


def compute_player_metrics(
    events: pd.DataFrame, player: str | None, player_id: int | None = None
) -> dict:
    player = _resolve_player(events, player, player_id)
    if not player:
        return {}
    player_events = events[events["player"] == player]
    if player_id is not None and "player_id" in events.columns:
        by_id = events[events["player_id"] == player_id]
        if len(by_id) > 0:
            player_events = by_id
    if len(player_events) == 0:
        return {}

    minutes = _infer_minutes(events, player)
    if minutes == 0:
        return {}

    p90 = lambda v: round(v / minutes * 90, 2) if minutes > 0 else 0

    shots = player_events[player_events["type"] == "Shot"]
    passes = player_events[player_events["type"] == "Pass"]
    carries = player_events[player_events["type"] == "Carry"]
    dribbles = player_events[player_events["type"] == "Dribble"]
    duels = player_events[player_events["type"] == "Duel"]
    pressures = player_events[player_events["type"] == "Pressure"]
    interceptions = player_events[player_events["type"] == "Interception"]
    clearances = player_events[player_events["type"] == "Clearance"]
    blocks = player_events[player_events["type"] == "Block"]
    recoveries = player_events[player_events["type"] == "Ball Recovery"]
    fouls_committed = player_events[player_events["type"] == "Foul Committed"]
    fouls_won = player_events[player_events["type"] == "Foul Won"]
    dispossessed = player_events[player_events["type"] == "Dispossessed"]
    miscontrols = player_events[player_events["type"] == "Miscontrol"]
    dribbled_past = player_events[player_events["type"] == "Dribbled Past"]

    num_shots = len(shots)
    shot_outcome = _col(shots, "shot_outcome")
    goals = len(shots[shot_outcome == "Goal"])
    shots_ot = len(shots[shot_outcome.isin(["Goal", "Saved"])])
    xg_col = _col(shots, "shot_statsbomb_xg")
    xg_raw = xg_col.sum()
    xg = round(xg_raw if pd.notna(xg_raw) else 0, 2)

    num_passes = len(passes)
    pass_outcome = _col(passes, "pass_outcome")
    num_completed = len(passes[pass_outcome.isna()])
    pass_pct = percentage(num_completed, num_passes)

    shot_assist = _col(passes, "pass_shot_assist").eq(True)
    key_passes = int(shot_assist.sum())
    goal_assist = _col(passes, "pass_goal_assist").eq(True)
    all_shots = events[events["type"] == "Shot"]
    all_shot_outcomes = _col(all_shots, "shot_outcome")
    goal_shot_ids = (
        set(all_shots.loc[all_shot_outcomes == "Goal", "id"].dropna())
        if "id" in all_shots
        else set()
    )
    assisted_shot_ids = set(
        _col(passes.loc[goal_assist], "pass_assisted_shot_id").dropna()
    )
    assists = len(goal_shot_ids & assisted_shot_ids)

    xa = 0
    shot_assist_passes = passes[shot_assist] if "pass_shot_assist" in passes else passes.iloc[0:0]
    for _, pk in shot_assist_passes.iterrows():
        shot_id = pk.get("pass_assisted_shot_id")
        if pd.notna(shot_id):
            assisted = all_shots[all_shots["id"] == shot_id]
            if len(assisted) > 0:
                val = assisted.iloc[0].get("shot_statsbomb_xg")
                if pd.notna(val):
                    xa += val
    xa = round(xa, 2)

    progressive_passes = 0
    passes_into_final_third = 0
    passes_into_final_third_completed = 0
    if "location" in passes.columns and "pass_end_location" in passes.columns:
        locations = passes["location"]
        end_locations = passes["pass_end_location"]
        outcomes = _col(passes, "pass_outcome")
        for start, end, outcome in zip(locations, end_locations, outcomes):
            if not isinstance(start, (list, tuple)) or not isinstance(end, (list, tuple)):
                continue
            try:
                start_x = float(start[0])
                end_x = float(end[0])
            except (IndexError, TypeError, ValueError):
                continue
            if pd.isna(start_x) or pd.isna(end_x):
                continue
            if end_x > FINAL_THIRD_X:
                passes_into_final_third += 1
                if pd.isna(outcome):
                    passes_into_final_third_completed += 1
            if pd.notna(outcome) or end_x <= start_x:
                continue
            distance = end_x - start_x
            if start_x < 60:
                threshold = 15 if end_x >= 60 else 30
            else:
                threshold = MIN_PROGRESSIVE_DIST
            if distance >= threshold:
                progressive_passes += 1

    pass_cross = _col(passes, "pass_cross")
    crosses = len(passes[pass_cross == True])
    pass_tb = _col(passes, "pass_through_ball")
    through_balls = len(passes[pass_tb == True])
    pass_sw = _col(passes, "pass_switch")
    switches = len(passes[pass_sw == True])

    num_dribbles = len(dribbles)
    drib_outcome = _col(dribbles, "dribble_outcome")
    completed_dribbles = len(dribbles[drib_outcome == "Complete"])
    dribble_pct = percentage(completed_dribbles, num_dribbles)

    # Vectorized progressive carries (avoids O(n) iterrows)
    num_carries = len(carries)
    progressive_carries = 0
    if "location" in carries.columns and "carry_end_location" in carries.columns:
        locs = carries["location"].dropna()
        ends = carries["carry_end_location"].dropna()
        idx = locs.index.intersection(ends.index)
        if len(idx) > 0:
            dx_series = pd.Series(
                [ends[i][0] - locs[i][0] for i in idx], index=idx
            )
            progressive_carries = int((dx_series > MIN_PROGRESSIVE_DIST).sum())

    num_duels = len(duels)
    duel_outcome = _col(duels, "duel_outcome")
    won_conditions = duel_outcome.isin(["Won", "Success In Play", "Success Out"])
    duels_won = len(duels[won_conditions])
    duel_pct = percentage(duels_won, num_duels)

    duel_type = _col(duels, "duel_type")
    tackles = len(duels[duel_type == "Tackle"])
    tackles_won = len(
        duels[(duel_type == "Tackle") & won_conditions]
    )
    tackle_pct = percentage(tackles_won, tackles)

    # StatsBomb only logs the duel for the player who loses it; the winner is
    # flagged on the next action (pass, clearance or shot made after the header).
    aerial_mask = duel_type.astype("string").str.contains("Aerial", case=False, na=False)
    aerial_lost = len(duels[aerial_mask])
    aerial_won = sum(
        int(_col(player_events, flag).eq(True).sum()) for flag in AERIAL_WON_FLAGS
    )
    aerial_duels = aerial_lost + aerial_won
    aerial_pct = percentage(aerial_won, aerial_duels)

    return {
        "player": player,
        "minutes": int(minutes),
        "goals": int(goals),
        "assists": int(assists),
        "shots": int(num_shots),
        "shots_on_target": int(shots_ot),
        "shot_accuracy": percentage(shots_ot, num_shots),
        "xg": xg,
        "xg_per_90": p90(xg),
        "xa": xa,
        "xa_per_90": p90(xa),
        "goals_per_90": p90(goals),
        "passes": int(num_passes),
        "passes_completed": int(num_completed),
        "pass_completion_pct": pass_pct,
        "key_passes": int(key_passes),
        "progressive_passes": int(progressive_passes),
        "passes_into_final_third": int(passes_into_final_third),
        "passes_into_final_third_completed": int(passes_into_final_third_completed),
        "passes_into_final_third_pct": percentage(
            passes_into_final_third_completed, passes_into_final_third
        ),
        "crosses": int(crosses),
        "through_balls": int(through_balls),
        "switches": int(switches),
        "dribbles": int(num_dribbles),
        "dribbles_completed": int(completed_dribbles),
        "dribble_success_pct": dribble_pct,
        "carries": int(num_carries),
        "progressive_carries": int(progressive_carries),
        "duels": int(num_duels),
        "duels_won": int(duels_won),
        "duel_success_pct": duel_pct,
        "tackles": int(tackles),
        "tackles_won": int(tackles_won),
        "tackle_success_pct": tackle_pct,
        "aerial_duels": int(aerial_duels),
        "aerial_duels_won": int(aerial_won),
        "aerial_success_pct": aerial_pct,
        "pressures": int(len(pressures)),
        "interceptions": int(len(interceptions)),
        "clearances": int(len(clearances)),
        "blocks": int(len(blocks)),
        "ball_recoveries": int(len(recoveries)),
        "fouls_committed": int(len(fouls_committed)),
        "fouls_won": int(len(fouls_won)),
        "dispossessed": int(len(dispossessed)),
        "miscontrols": int(len(miscontrols)),
        "dribbled_past": int(len(dribbled_past)),
    }


@lru_cache(maxsize=4096)
def has_player_metrics(player_id: int) -> bool:
    for folder in (METRICS_DIR, SAMPLE_DATA_DIR):
        path = folder / f"metrics_{player_id}.json"
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                return bool(json.load(f))
        except (json.JSONDecodeError, OSError):
            return False
    return False


def get_match_metrics(match_id: int) -> list[dict]:
    events = get_match_events(match_id)
    if len(events) == 0:
        return []
    players = events["player"].dropna().unique()
    results = []
    for p in sorted(players):
        metrics = compute_player_metrics(events, p)
        if metrics:
            results.append(metrics)
    return results


@lru_cache(maxsize=512)
def get_player_metrics_across_matches(player_id: int) -> list[dict]:
    """Compute per-match metrics for a player, cached in memory (512 slots) and persisted to disk."""
    # Check disk cache first (survives restarts)
    cache_path = METRICS_DIR / f"metrics_{player_id}.json"
    if settings.demo_mode and not cache_path.exists():
        for folder in (SAMPLE_DATA_DIR, METRICS_DIR):
            candidate = folder / cache_path.name
            if candidate.exists():
                cache_path = candidate
                break
    if cache_path.exists():
        try:
            import json
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not settings.demo_mode or data:
                return [_normalize_pct_fields(dict(row)) for row in data]
        except (json.JSONDecodeError, IOError):
            cache_path.unlink(missing_ok=True)

    if settings.demo_mode:
        return []

    from app.services.statsbomb import search_players

    player_rows = search_players(limit=10000)
    player_rows = player_rows[player_rows["player_id"] == player_id]
    if len(player_rows) == 0:
        return []

    player_name = player_rows.iloc[0]["player_name"]
    match_ids = player_rows["match_id"].unique()

    def find_player_in_events(events_df, name, pid):
        matched = _resolve_player(events_df, None, pid)
        if matched is not None:
            return matched
        if name in events_df["player"].values:
            return name
        for p in events_df["player"].dropna().unique():
            if name in p or p in name:
                return p
        return None

    all_metrics = []
    for mid in match_ids:
        events = get_match_events(int(mid))
        matched_name = find_player_in_events(events, player_name, player_id)
        if matched_name is None:
            continue
        metrics = compute_player_metrics(events, matched_name, player_id)
        if metrics:
            match_info = player_rows[player_rows["match_id"] == mid].iloc[0]
            metrics["match_id"] = int(mid)
            metrics["team"] = match_info.get("team", "")
            metrics["competition"] = match_info.get("competition", "")
            metrics["season"] = match_info.get("season", "")
            all_metrics.append(metrics)

    # Persist to disk so 2nd request is instant (even after restart)
    try:
        import json
        tmp = cache_path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(all_metrics, f, default=str)
        tmp.replace(cache_path)
    except IOError:
        pass

    return all_metrics


@lru_cache(maxsize=2)
def compute_position_averages(player_name: str) -> dict:
    """Get league-wide averages from the pre-computed Vector DB (instant)."""
    from app.services.similarity import get_global_averages
    return get_global_averages()

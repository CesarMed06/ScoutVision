from functools import lru_cache

import pandas as pd

from app.services.statsbomb import get_match_events, search_players

FINAL_THIRD_X = 80
MIN_PROGRESSIVE_DIST = 10


def _infer_minutes(events: pd.DataFrame, player: str) -> float:
    subs = events[events["type"] == "Substitution"]
    subbed_on = subs[subs["substitution_replacement"] == player]
    subbed_off = subs[subs["player"] == player]
    player_events = events[events["player"] == player]
    if len(player_events) == 0:
        return 0
    first_half_end = events[(events["type"] == "Half End") & (events["period"] == 1)]
    full_time = 90
    if len(first_half_end) > 0:
        full_time = int(first_half_end.iloc[0]["minute"]) * 2
    else:
        full_time = int(player_events["minute"].max()) + 5
    full_time = max(full_time, 90)
    has_starting_xi = len(player_events[player_events["minute"] <= 1]) > 0
    if len(subbed_on) > 0:
        start_min = int(subbed_on.iloc[0]["minute"])
    elif has_starting_xi:
        start_min = 0
    else:
        start_min = int(player_events["minute"].min())
    if len(subbed_off) > 0:
        end_min = int(subbed_off.iloc[0]["minute"])
    else:
        end_min = full_time
    return max(0, end_min - start_min)


def _col(df, name):
    return df[name] if name in df.columns else pd.Series(index=df.index, dtype=float)


def compute_player_metrics(events: pd.DataFrame, player: str) -> dict:
    player_events = events[events["player"] == player]
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
    shots_ot = len(shots[shot_outcome.isin(["Goal", "Saved", "Post"])])
    xg_col = _col(shots, "shot_statsbomb_xg")
    xg_raw = xg_col.sum()
    xg = round(xg_raw if pd.notna(xg_raw) else 0, 2)

    num_passes = len(passes)
    pass_outcome = _col(passes, "pass_outcome")
    num_completed = len(passes[pass_outcome.isna()])
    pass_pct = round(num_completed / num_passes * 100, 1) if num_passes > 0 else 0

    shot_assist = _col(passes, "pass_shot_assist")
    key_passes = len(passes[shot_assist.notna()])
    goal_assist = _col(passes, "pass_goal_assist")
    assists = len(passes[goal_assist.notna()])

    xa = 0
    for _, pk in passes[shot_assist.notna()].iterrows():
        shot_id = pk.get("pass_assisted_shot_id")
        if pd.notna(shot_id):
            assisted = shots[shots["id"] == shot_id]
            if len(assisted) > 0:
                val = assisted.iloc[0].get("shot_statsbomb_xg")
                if pd.notna(val):
                    xa += val
    xa = round(xa, 2)

    progressive_passes = 0
    passes_into_final_third = 0
    for _, p in passes.iterrows():
        loc = p.get("location")
        end_loc = p.get("pass_end_location")
        if (
            isinstance(loc, (list, tuple))
            and len(loc) >= 2
            and isinstance(end_loc, (list, tuple))
            and len(end_loc) >= 2
        ):
            dx = end_loc[0] - loc[0]
            if dx > MIN_PROGRESSIVE_DIST:
                progressive_passes += 1
            if end_loc[0] > FINAL_THIRD_X:
                passes_into_final_third += 1

    pass_cross = _col(passes, "pass_cross")
    crosses = len(passes[pass_cross == True])
    pass_tb = _col(passes, "pass_through_ball")
    through_balls = len(passes[pass_tb == True])
    pass_sw = _col(passes, "pass_switch")
    switches = len(passes[pass_sw == True])

    num_dribbles = len(dribbles)
    drib_outcome = _col(dribbles, "dribble_outcome")
    completed_dribbles = len(dribbles[drib_outcome == "Complete"])
    dribble_pct = (
        round(completed_dribbles / num_dribbles * 100, 1)
        if num_dribbles > 0
        else 0
    )

    num_carries = len(carries)
    progressive_carries = 0
    for _, c in carries.iterrows():
        loc = c.get("location")
        end_loc = c.get("carry_end_location")
        if (
            isinstance(loc, (list, tuple))
            and len(loc) >= 2
            and isinstance(end_loc, (list, tuple))
            and len(end_loc) >= 2
        ):
            if end_loc[0] - loc[0] > MIN_PROGRESSIVE_DIST:
                progressive_carries += 1

    num_duels = len(duels)
    duel_outcome = _col(duels, "duel_outcome")
    won_conditions = duel_outcome.isin(["Won", "Success In Play", "Success Out"])
    duels_won = len(duels[won_conditions])
    duel_pct = round(duels_won / num_duels * 100, 1) if num_duels > 0 else 0

    duel_type = _col(duels, "duel_type")
    tackles = len(duels[duel_type == "Tackle"])
    tackles_won = len(
        duels[(duel_type == "Tackle") & won_conditions]
    )
    tackle_pct = round(tackles_won / tackles * 100, 1) if tackles > 0 else 0

    aerial_mask = duel_type.str.contains("Aerial", case=False, na=False)
    aerial_duels = len(duels[aerial_mask])
    aerial_won = len(
        duels[aerial_mask & duel_outcome.isin(["Won", "Success Out"])]
    )
    aerial_pct = round(aerial_won / aerial_duels * 100, 1) if aerial_duels > 0 else 0

    return {
        "player": player,
        "minutes": int(minutes),
        "goals": int(goals),
        "assists": int(assists),
        "shots": int(num_shots),
        "shots_on_target": int(shots_ot),
        "shot_accuracy": round(shots_ot / num_shots * 100, 1) if num_shots > 0 else 0,
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


@lru_cache(maxsize=64)
def get_player_metrics_across_matches(player_id: int) -> list[dict]:
    from app.services.statsbomb import search_players

    player_rows = search_players(limit=10000)
    player_rows = player_rows[player_rows["player_id"] == player_id]
    if len(player_rows) == 0:
        return []

    player_name = player_rows.iloc[0]["player_name"]
    match_ids = player_rows["match_id"].unique()

    def find_player_in_events(events_df, name):
        if name in events_df["player"].values:
            return name
        for p in events_df["player"].dropna().unique():
            if name in p or p in name:
                return p
        return None

    all_metrics = []
    for mid in match_ids:
        events = get_match_events(int(mid))
        matched_name = find_player_in_events(events, player_name)
        if matched_name is None:
            continue
        metrics = compute_player_metrics(events, matched_name)
        if metrics:
            match_info = player_rows[player_rows["match_id"] == mid].iloc[0]
            metrics["match_id"] = int(mid)
            metrics["team"] = match_info.get("team", "")
            metrics["competition"] = match_info.get("competition", "")
            metrics["season"] = match_info.get("season", "")
            all_metrics.append(metrics)
    return all_metrics


@lru_cache(maxsize=16)
def compute_position_averages(player_name: str) -> dict:
    df = search_players(limit=10000)
    seen = set()
    names = []
    for _, row in df.iterrows():
        pid = row["player_id"]
        if pid not in seen:
            seen.add(pid)
            names.append(row["player_name"])

    totals = {}
    count = 0
    radar_keys = [
        "goals_per_90", "xg_per_90", "xa_per_90",
        "key_passes_per_90", "dribbles_per_90",
        "pass_completion_pct", "tackles_per_90", "aerial_success_pct",
    ]

    for k in radar_keys:
        totals[k] = 0

    for name in names[:100]:
        if name == player_name:
            continue
        try:
            metrics_list = get_player_metrics_across_matches(
                int(df[df["player_name"] == name].iloc[0]["player_id"])
            )
        except (IndexError, ValueError, TypeError):
            continue
        if not metrics_list:
            continue
        t = {}
        skip = {"player", "match_id", "team", "competition", "season"}
        for key in metrics_list[0]:
            if key in skip:
                continue
            if key.endswith("_pct") or key.endswith("_per_90"):
                continue
            t[key] = sum(m.get(key, 0) or 0 for m in metrics_list)
        min_t = t.get("minutes", 0) or 1
        p90 = lambda v: round(v / min_t * 90, 2)
        t["goals_per_90"] = p90(t.get("goals", 0))
        t["xg_per_90"] = p90(t.get("xg", 0))
        t["xa_per_90"] = p90(t.get("xa", 0))
        t["key_passes_per_90"] = p90(t.get("key_passes", 0))
        t["dribbles_per_90"] = p90(t.get("dribbles", 0))
        t["tackles_per_90"] = p90(t.get("tackles", 0))
        shots = t.get("shots", 0) or 1
        t["pass_completion_pct"] = round(t.get("passes_completed", 0) / (t.get("passes", 0) or 1) * 100, 1)
        aerials = t.get("aerial_duels", 0) or 1
        t["aerial_success_pct"] = round(t.get("aerial_duels_won", 0) / aerials * 100, 1)

        for k in radar_keys:
            totals[k] += t.get(k, 0)
        count += 1

    if count == 0:
        return {k: 50 for k in radar_keys}

    avgs = {k: round(totals[k] / count, 2) for k in radar_keys}
    avgs["players_sampled"] = count
    return avgs

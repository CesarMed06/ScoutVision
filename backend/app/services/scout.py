import app.services.similarity as sim


def scout_players(
    min_goals_per_90: float = 0,
    min_xg_per_90: float = 0,
    min_xa_per_90: float = 0,
    min_key_passes_per_90: float = 0,
    min_tackles_per_90: float = 0,
    min_pass_pct: float = 0,
    min_dribble_pct: float = 0,
    min_aerial_pct: float = 0,
    min_pressures_per_90: float = 0,
    sort_by: str = "goals_per_90",
    sort_dir: str = "desc",
    limit: int = 50,
) -> list[dict]:
    results = []
    for pid, data in sim.VECTOR_DB.items():
        totals = data.get("totals", {})
        if not totals:
            continue

        minutes = totals.get("minutes", 0) or 1
        p90 = lambda v: round(v / minutes * 90, 2) if minutes > 0 else 0

        row = {
            "player_id": pid,
            "player_name": data["name"],
            "team": data["player_info"].get("team", ""),
            "competition": data["player_info"].get("competition", ""),
            "matches": int(totals.get("matches", 0)),
            "minutes": int(minutes),
            "goals_per_90": p90(totals.get("goals", 0)),
            "xg_per_90": p90(totals.get("xg", 0)),
            "xa_per_90": p90(totals.get("xa", 0)),
            "key_passes_per_90": p90(totals.get("key_passes", 0)),
            "tackles_per_90": p90(totals.get("tackles", 0)),
            "pressures_per_90": p90(totals.get("pressures", 0)),
            "pass_pct": round(totals.get("passes_completed", 0) / (totals.get("passes", 0) or 1) * 100, 1),
            "dribble_pct": round(totals.get("dribbles_completed", 0) / (totals.get("dribbles", 0) or 1) * 100, 1),
            "aerial_pct": round(totals.get("aerial_duels_won", 0) / (totals.get("aerial_duels", 0) or 1) * 100, 1),
        }

        # Apply filters
        if row["goals_per_90"] < min_goals_per_90: continue
        if row["xg_per_90"] < min_xg_per_90: continue
        if row["xa_per_90"] < min_xa_per_90: continue
        if row["key_passes_per_90"] < min_key_passes_per_90: continue
        if row["tackles_per_90"] < min_tackles_per_90: continue
        if row["pass_pct"] < min_pass_pct: continue
        if row["dribble_pct"] < min_dribble_pct: continue
        if row["aerial_pct"] < min_aerial_pct: continue
        if row["pressures_per_90"] < min_pressures_per_90: continue

        results.append(row)

    # Sort
    reverse = sort_dir == "desc"
    results.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)

    return results[:limit]

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.services.metrics import get_player_metrics_across_matches
from app.services.statsbomb import search_players

METRIC_KEYS = [
    "goals_per_90", "xg_per_90", "xa_per_90",
    "key_passes_per_90", "progressive_passes_per_90",
    "dribbles_per_90", "dribble_success_pct",
    "pass_completion_pct", "tackles_per_90",
    "aerial_success_pct", "pressures_per_90",
]


def _compute_vector(metrics_list: list[dict]) -> list[float]:
    if not metrics_list:
        return [0] * len(METRIC_KEYS)
    totals = {}
    skip = {"player", "match_id", "team", "competition", "season"}
    for key in metrics_list[0]:
        if key in skip:
            continue
        if key.endswith("_pct") or key.endswith("_per_90"):
            continue
        totals[key] = sum(m.get(key, 0) or 0 for m in metrics_list)
    minutes = totals.get("minutes", 0) or 1
    p90 = lambda v: round(v / minutes * 90, 2)
    vec = {
        "goals_per_90": p90(totals.get("goals", 0)),
        "xg_per_90": p90(totals.get("xg", 0)),
        "xa_per_90": p90(totals.get("xa", 0)),
        "key_passes_per_90": p90(totals.get("key_passes", 0)),
        "progressive_passes_per_90": p90(totals.get("progressive_passes", 0)),
        "dribbles_per_90": p90(totals.get("dribbles", 0)),
        "dribble_success_pct": round(totals.get("dribbles_completed", 0) / (totals.get("dribbles", 0) or 1) * 100, 1),
        "pass_completion_pct": round(totals.get("passes_completed", 0) / (totals.get("passes", 0) or 1) * 100, 1),
        "tackles_per_90": p90(totals.get("tackles", 0)),
        "aerial_success_pct": round(totals.get("aerial_duels_won", 0) / (totals.get("aerial_duels", 0) or 1) * 100, 1),
        "pressures_per_90": p90(totals.get("pressures", 0)),
    }
    return [vec.get(k, 0) for k in METRIC_KEYS]


def get_similar_players(player_id: int, top_n: int = 10) -> list[dict]:
    target_metrics = get_player_metrics_across_matches(player_id)
    if not target_metrics:
        return []
    target_vec = np.array(_compute_vector(target_metrics)).reshape(1, -1)

    df = search_players(limit=10000)
    seen = set()
    candidates = []
    for _, row in df.iterrows():
        pid = row["player_id"]
        if pid not in seen:
            seen.add(pid)
            candidates.append((pid, row["player_name"]))

    results = []
    for pid, name in candidates[:50]:
        if pid == player_id:
            continue
        try:
            metrics = get_player_metrics_across_matches(pid)
        except Exception:
            continue
        if not metrics:
            continue
        vec = np.array(_compute_vector(metrics)).reshape(1, -1)
        if np.linalg.norm(vec) == 0:
            continue
        sim = cosine_similarity(target_vec, vec)[0][0]
        if np.isnan(sim):
            continue
        results.append({
            "player_id": pid,
            "player_name": name,
            "similarity": round(float(sim), 4),
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_n]

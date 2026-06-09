import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.services.metrics import get_player_metrics_across_matches

METRIC_KEYS = [
    "goals_per_90", "xg_per_90", "xa_per_90",
    "key_passes_per_90", "progressive_passes_per_90",
    "dribbles_per_90", "dribble_success_pct",
    "pass_completion_pct", "tackles_per_90",
    "aerial_success_pct", "pressures_per_90",
]

# In-memory vector database: {player_id: {"vector": [...], "name": str, "totals": {...}, "player_info": {...}}}
VECTOR_DB: dict[int, dict] = {}
_VECTOR_DB_INITIALIZED = False


def _accumulate_totals(metrics_list: list[dict]) -> dict:
    """Accumulate raw totals from per-match metrics, skipping computed fields."""
    totals = {}
    skip_cols = {"player", "match_id", "team", "competition", "season"}
    for key in metrics_list[0]:
        if key in skip_cols:
            continue
        if key.endswith("_pct") or key.endswith("_per_90"):
            continue
        totals[key] = sum(m.get(key, 0) or 0 for m in metrics_list)
    return totals


def _compute_vector_from_totals(totals: dict) -> list[float]:
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


def _compute_vector(metrics_list: list[dict]) -> list[float]:
    if not metrics_list:
        return [0] * len(METRIC_KEYS)
    return _compute_vector_from_totals(_accumulate_totals(metrics_list))


def init_vector_db(max_players: int = 2000):
    """Pre-compute vectors + full totals for all players and store in memory."""
    from app.services.statsbomb import search_players

    global VECTOR_DB, _VECTOR_DB_INITIALIZED
    if _VECTOR_DB_INITIALIZED:
        return

    df = search_players(limit=10000)
    seen = set()
    pids = []
    for _, row in df.iterrows():
        pid = row["player_id"]
        if pid not in seen:
            seen.add(pid)
            pids.append(pid)

    count = 0
    for pid in pids[:max_players]:
        try:
            metrics = get_player_metrics_across_matches(int(pid))
            if metrics:
                totals = _accumulate_totals(metrics)
                vec = _compute_vector_from_totals(totals)
                VECTOR_DB[int(pid)] = {
                    "vector": vec,
                    "name": metrics[0]["player"],
                    "totals": totals,
                    "player_info": {
                        "player_id": int(pid),
                        "player_name": metrics[0]["player"],
                        "team": metrics[0].get("team", ""),
                        "competition": metrics[0].get("competition", ""),
                    },
                }
                count += 1
        except Exception:
            continue

    _VECTOR_DB_INITIALIZED = True


def get_similar_players(player_id: int, top_n: int = 10) -> list[dict]:
    # Ensure vector DB is initialized
    if not _VECTOR_DB_INITIALIZED:
        init_vector_db()
    
    target_metrics = get_player_metrics_across_matches(player_id)
    if not target_metrics:
        return []
    target_vec = np.array(_compute_vector(target_metrics)).reshape(1, -1)
    
    results = []
    for pid, data in VECTOR_DB.items():
        if pid == player_id:
            continue
        vec = np.array(data["vector"]).reshape(1, -1)
        if np.linalg.norm(vec) == 0:
            continue
        sim = cosine_similarity(target_vec, vec)[0][0]
        if np.isnan(sim):
            continue
        results.append({
            "player_id": pid,
            "player_name": data["name"],
            "similarity": round(float(sim), 4),
        })
    
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_n]

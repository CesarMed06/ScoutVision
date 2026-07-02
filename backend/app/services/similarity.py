import json
import logging
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.services.metrics import get_player_metrics_across_matches

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
VECTOR_DB_PATH = DATA_DIR / "vector_db.json"

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


def _load_vector_db() -> bool:
    """Load VECTOR_DB from disk if it exists (survives restarts)."""
    global VECTOR_DB, _VECTOR_DB_INITIALIZED
    if VECTOR_DB_PATH.exists():
        try:
            with open(VECTOR_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            VECTOR_DB = {int(k): v for k, v in data.items()}
            _VECTOR_DB_INITIALIZED = True
            logger.info(f"Loaded Vector DB from disk: {len(VECTOR_DB)} players")
            return True
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Vector DB file corrupted, rebuilding: {e}")
            VECTOR_DB_PATH.unlink(missing_ok=True)
    return False


def _save_vector_db():
    """Persist VECTOR_DB to disk so it survives restarts."""
    try:
        tmp = VECTOR_DB_PATH.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in VECTOR_DB.items()}, f)
        tmp.replace(VECTOR_DB_PATH)
        logger.info(f"Vector DB saved to disk: {len(VECTOR_DB)} players")
    except Exception as e:
        logger.error(f"Failed to save Vector DB: {e}")


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
    """Pre-compute vectors + full totals for all players and store in memory.
    Loads from disk first if available (instant on restart)."""
    global VECTOR_DB, _VECTOR_DB_INITIALIZED
    if _VECTOR_DB_INITIALIZED:
        return

    # Try loading from disk first (survives restarts)
    if _load_vector_db():
        return

    from app.services.statsbomb import search_players

    df = search_players(limit=10000)
    seen = set()
    pids_with_pos = {}  # pid -> position
    for _, row in df.iterrows():
        pid = row["player_id"]
        if pid not in seen:
            seen.add(pid)
            pids_with_pos[pid] = row.get("position", "")

    count = 0
    for pid in list(pids_with_pos.keys())[:max_players]:
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
                        "position": pids_with_pos.get(pid, ""),
                    },
                }
                count += 1
                if count % 100 == 0:
                    logger.info(f"Vector DB: {count}/{min(len(pids_with_pos), max_players)} players indexed...")
        except Exception:
            continue

    logger.info(f"Vector DB build complete: {count} players indexed")
    _VECTOR_DB_INITIALIZED = True
    # Persist to disk so restarts are instant
    _save_vector_db()


def get_similar_players(player_id: int, top_n: int = 10, position_filter: str | None = None) -> list[dict]:
    # Don't block the request thread — return empty if DB isn't ready yet (it builds in background)
    if not _VECTOR_DB_INITIALIZED:
        logger.info("Vector DB not yet initialized, returning empty similarity results")
        return []
    
    target_metrics = get_player_metrics_across_matches(player_id)
    if not target_metrics:
        return []
    target_vec = np.array(_compute_vector(target_metrics)).reshape(1, -1)
    
    results = []
    for pid, data in VECTOR_DB.items():
        if pid == player_id:
            continue
        if position_filter:
            player_pos = data.get("player_info", {}).get("position", "")
            if not player_pos or position_filter.lower() not in player_pos.lower():
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


RADAR_KEYS = [
    "goals_per_90", "xg_per_90", "xa_per_90",
    "key_passes_per_90", "dribbles_per_90",
    "tackles_per_90",
]

PCT_KEYS = ["pass_completion_pct", "aerial_success_pct"]


def get_global_averages() -> dict:
    """Compute league-wide averages from VECTOR_DB totals (instant).
    Returns zero-filled dict if DB isn't ready yet (builds in background)."""
    if not _VECTOR_DB_INITIALIZED:
        logger.info("Vector DB not yet initialized, returning zero-filled averages")
        return {k: 0 for k in (RADAR_KEYS + PCT_KEYS)}
    
    totals = {k: 0.0 for k in (RADAR_KEYS + PCT_KEYS)}
    # Accumulate raw sums for percentage metrics (don't average per-player %)
    sum_passes_completed = 0
    sum_passes = 0
    sum_aerial_won = 0
    sum_aerials = 0
    count = 0
    
    for pid, data in VECTOR_DB.items():
        player_totals = data.get("totals", {})
        minutes = player_totals.get("minutes", 0) or 1
        
        totals["goals_per_90"] += round(player_totals.get("goals", 0) / minutes * 90, 2)
        totals["xg_per_90"] += round(player_totals.get("xg", 0) / minutes * 90, 2)
        totals["xa_per_90"] += round(player_totals.get("xa", 0) / minutes * 90, 2)
        totals["key_passes_per_90"] += round(player_totals.get("key_passes", 0) / minutes * 90, 2)
        totals["dribbles_per_90"] += round(player_totals.get("dribbles", 0) / minutes * 90, 2)
        totals["tackles_per_90"] += round(player_totals.get("tackles", 0) / minutes * 90, 2)
        
        # Accumulate raw totals for correct percentage averaging
        sum_passes_completed += player_totals.get("passes_completed", 0)
        sum_passes += player_totals.get("passes", 0)
        sum_aerial_won += player_totals.get("aerial_duels_won", 0)
        sum_aerials += player_totals.get("aerial_duels", 0)
        
        count += 1

    if count == 0:
        return {k: 0 for k in (RADAR_KEYS + PCT_KEYS)}

    avgs = {k: round(totals[k] / count, 2) for k in (RADAR_KEYS + PCT_KEYS)}
    # Correct percentage averages: sum(raw) / sum(total), not avg of per-player %
    avgs["pass_completion_pct"] = round(sum_passes_completed / (sum_passes or 1) * 100, 1)
    avgs["aerial_success_pct"] = round(sum_aerial_won / (sum_aerials or 1) * 100, 1)
    avgs["players_sampled"] = count
    return avgs

from fastapi import APIRouter, HTTPException

from app.services import metrics as metrics_service

router = APIRouter()


@router.get("/match/{match_id}")
def get_match_metrics(match_id: int):
    result = metrics_service.get_match_metrics(match_id)
    if not result:
        raise HTTPException(status_code=404, detail="No metrics found for this match")
    return result


@router.get("/player/{player_id}")
def get_player_metrics(player_id: int):
    result = metrics_service.get_player_metrics_across_matches(player_id)
    if not result:
        raise HTTPException(
            status_code=404, detail="No metrics found for this player"
        )
    return {
        "player_id": player_id,
        "player_name": result[0]["player"],
        "matches": len(result),
        "match_details": result,
        "totals": _aggregate_totals(result),
    }


@router.get("/averages/{player_name}")
def get_position_averages(player_name: str):
    averages = metrics_service.compute_position_averages(player_name)
    return averages


def _aggregate_totals(match_list: list[dict]) -> dict:
    if not match_list:
        return {}
    totals = {}
    skip_keys = {"player", "match_id", "team", "competition", "season"}
    for key in match_list[0]:
        if key in skip_keys:
            continue
        if key.endswith("_pct") or key.endswith("_per_90"):
            continue
        totals[key] = sum(m.get(key, 0) or 0 for m in match_list)

    totals["matches"] = len(match_list)
    total_minutes = totals.get("minutes", 0) or 1
    p90 = lambda v: round(v / total_minutes * 90, 2)

    totals["xg"] = round(totals.get("xg", 0), 2)
    totals["xa"] = round(totals.get("xa", 0), 2)
    totals["goals_per_90"] = p90(totals.get("goals", 0))
    totals["xg_per_90"] = p90(totals.get("xg", 0))
    totals["xa_per_90"] = p90(totals.get("xa", 0))
    totals["shots_per_90"] = p90(totals.get("shots", 0))
    totals["passes_per_90"] = p90(totals.get("passes", 0))
    totals["key_passes_per_90"] = p90(totals.get("key_passes", 0))
    totals["progressive_passes_per_90"] = p90(
        totals.get("progressive_passes", 0)
    )
    totals["dribbles_per_90"] = p90(totals.get("dribbles", 0))
    totals["carries_per_90"] = p90(totals.get("carries", 0))
    totals["pressures_per_90"] = p90(totals.get("pressures", 0))
    totals["tackles_per_90"] = p90(totals.get("tackles", 0))

    shots = totals.get("shots", 0) or 1
    totals["shot_accuracy"] = round(
        totals.get("shots_on_target", 0) / shots * 100, 1
    )
    passes = totals.get("passes", 0) or 1
    totals["pass_completion_pct"] = round(
        totals.get("passes_completed", 0) / passes * 100, 1
    )
    dribbles = totals.get("dribbles", 0) or 1
    totals["dribble_success_pct"] = round(
        totals.get("dribbles_completed", 0) / dribbles * 100, 1
    )
    duels = totals.get("duels", 0) or 1
    totals["duel_success_pct"] = round(
        totals.get("duels_won", 0) / duels * 100, 1
    )
    tackles = totals.get("tackles", 0) or 1
    totals["tackle_success_pct"] = round(
        totals.get("tackles_won", 0) / tackles * 100, 1
    )
    aerials = totals.get("aerial_duels", 0) or 1
    totals["aerial_success_pct"] = round(
        totals.get("aerial_duels_won", 0) / aerials * 100, 1
    )

    return totals

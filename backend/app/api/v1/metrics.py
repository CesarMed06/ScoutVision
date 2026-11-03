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

    pct = metrics_service.percentage
    totals["shot_accuracy"] = pct(totals.get("shots_on_target", 0), totals.get("shots", 0))
    totals["pass_completion_pct"] = pct(
        totals.get("passes_completed", 0), totals.get("passes", 0)
    )
    totals["dribble_success_pct"] = pct(
        totals.get("dribbles_completed", 0), totals.get("dribbles", 0)
    )
    totals["duel_success_pct"] = pct(totals.get("duels_won", 0), totals.get("duels", 0))
    totals["tackle_success_pct"] = pct(
        totals.get("tackles_won", 0), totals.get("tackles", 0)
    )
    totals["aerial_success_pct"] = pct(
        totals.get("aerial_duels_won", 0), totals.get("aerial_duels", 0)
    )
    if "passes_into_final_third_completed" in totals:
        totals["passes_into_final_third_pct"] = pct(
            totals["passes_into_final_third_completed"],
            totals.get("passes_into_final_third", 0),
        )

    return totals

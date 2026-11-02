from typing import Literal

from fastapi import APIRouter, Query

from app.services.scout import scout_players

router = APIRouter()

SortField = Literal[
    "goals_per_90",
    "xg_per_90",
    "xa_per_90",
    "key_passes_per_90",
    "tackles_per_90",
    "pressures_per_90",
    "pass_pct",
    "dribble_pct",
    "aerial_pct",
]


@router.get("/players/search/advanced")
def advanced_scout(
    min_goals_per_90: float = Query(0, ge=0),
    min_xg_per_90: float = Query(0, ge=0),
    min_xa_per_90: float = Query(0, ge=0),
    min_key_passes_per_90: float = Query(0, ge=0),
    min_tackles_per_90: float = Query(0, ge=0),
    min_pass_pct: float = Query(0, ge=0, le=100),
    min_dribble_pct: float = Query(0, ge=0, le=100),
    min_aerial_pct: float = Query(0, ge=0, le=100),
    min_pressures_per_90: float = Query(0, ge=0),
    sort_by: SortField = "goals_per_90",
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
):
    return scout_players(
        min_goals_per_90=min_goals_per_90,
        min_xg_per_90=min_xg_per_90,
        min_xa_per_90=min_xa_per_90,
        min_key_passes_per_90=min_key_passes_per_90,
        min_tackles_per_90=min_tackles_per_90,
        min_pass_pct=min_pass_pct,
        min_dribble_pct=min_dribble_pct,
        min_aerial_pct=min_aerial_pct,
        min_pressures_per_90=min_pressures_per_90,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
    )

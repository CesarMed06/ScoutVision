from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import Response

from app.services import visualizations as viz_service

router = APIRouter()


@router.get("/viz/player/{player_id}/heatmap")
def get_player_heatmap(
    player_id: int = Path(..., gt=0), match_id: int = Query(..., gt=0)
):
    img = viz_service.player_heatmap(player_id, match_id)
    if img is None:
        raise HTTPException(
            status_code=404,
            detail="No heatmap data for this player in this match",
        )
    return Response(content=img, media_type="image/png")


@router.get("/viz/player/{player_id}/passes")
def get_player_passes(
    player_id: int = Path(..., gt=0), match_id: int = Query(..., gt=0)
):
    img = viz_service.player_passes(player_id, match_id)
    if img is None:
        raise HTTPException(
            status_code=404,
            detail="No pass data for this player in this match",
        )
    return Response(content=img, media_type="image/png")


@router.get("/viz/player/{player_id}/shots")
def get_player_shots(
    player_id: int = Path(..., gt=0), match_id: int = Query(..., gt=0)
):
    img = viz_service.player_shots(player_id, match_id)
    if img is None:
        raise HTTPException(
            status_code=404,
            detail="No shot data for this player in this match",
        )
    return Response(content=img, media_type="image/png")


@router.get("/viz/player/{player_id}/radar")
def get_player_radar(player_id: int = Path(..., gt=0)):
    img = viz_service.player_radar(player_id)
    if img is None:
        raise HTTPException(
            status_code=404,
            detail="No radar data for this player",
        )
    return Response(content=img, media_type="image/png")


@router.get("/viz/match/{match_id}/heatmap")
def get_match_heatmap(match_id: int = Path(..., gt=0)):
    img = viz_service.match_heatmap(match_id)
    if img is None:
        raise HTTPException(
            status_code=404,
            detail="No event data for this match",
        )
    return Response(content=img, media_type="image/png")

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.services import visualizations as viz_service

router = APIRouter()


@router.get("/viz/player/{player_id}/heatmap")
def get_player_heatmap(player_id: int, match_id: int = Query()):
    img = viz_service.player_heatmap(player_id, match_id)
    if img is None:
        return Response(status_code=404)
    return Response(content=img, media_type="image/png")


@router.get("/viz/player/{player_id}/passes")
def get_player_passes(player_id: int, match_id: int = Query()):
    img = viz_service.player_passes(player_id, match_id)
    if img is None:
        return Response(status_code=404)
    return Response(content=img, media_type="image/png")


@router.get("/viz/player/{player_id}/shots")
def get_player_shots(player_id: int, match_id: int = Query()):
    img = viz_service.player_shots(player_id, match_id)
    if img is None:
        return Response(status_code=404)
    return Response(content=img, media_type="image/png")


@router.get("/viz/player/{player_id}/radar")
def get_player_radar(player_id: int):
    img = viz_service.player_radar(player_id)
    if img is None:
        return Response(status_code=404)
    return Response(content=img, media_type="image/png")


@router.get("/viz/match/{match_id}/heatmap")
def get_match_heatmap(match_id: int):
    img = viz_service.match_heatmap(match_id)
    if img is None:
        return Response(status_code=404)
    return Response(content=img, media_type="image/png")

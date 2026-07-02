from fastapi import APIRouter, HTTPException, Query

from app.services.similarity import get_similar_players

router = APIRouter()


@router.get("/players/{player_id}/similar")
def get_players_similar(player_id: int, top_n: int = 10, position: str = Query(None)):
    result = get_similar_players(player_id, top_n, position_filter=position)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found or no similar players")
    return result

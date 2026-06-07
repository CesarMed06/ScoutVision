from fastapi import APIRouter, HTTPException

from app.services.similarity import get_similar_players

router = APIRouter()


@router.get("/players/{player_id}/similar")
def get_players_similar(player_id: int, top_n: int = 10):
    result = get_similar_players(player_id, top_n)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found or no similar players")
    return result

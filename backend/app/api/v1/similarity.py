from fastapi import APIRouter, HTTPException, Path, Query

from app.services.similarity import get_similar_players, vector_db_ready

router = APIRouter()


@router.get("/players/{player_id}/similar")
def get_players_similar(
    player_id: int = Path(..., gt=0),
    top_n: int = Query(10, ge=1, le=50),
    position: str | None = Query(None, max_length=40),
):
    if not vector_db_ready():
        raise HTTPException(status_code=503, detail="Similarity index is still building")
    result = get_similar_players(player_id, top_n, position_filter=position)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found or no similar players")
    return result

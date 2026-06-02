from fastapi import APIRouter, HTTPException, Query

from app.services.ai import generate_scouting_report

router = APIRouter()


@router.get("/players/{player_id}/report")
def get_player_report(player_id: int, lang: str = Query("en", regex="^(en|es)$")):
    report = generate_scouting_report(player_id, lang)
    if report is None:
        raise HTTPException(status_code=404, detail="Player not found")
    if report.startswith("GROQ_API_KEY") or report.startswith("GROQ_API_ERROR"):
        raise HTTPException(status_code=500, detail=report)
    if report.startswith("No match"):
        raise HTTPException(status_code=404, detail=report)
    return {
        "player_id": player_id,
        "language": lang,
        "report": report,
    }

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.services.ai import generate_scouting_report, generate_scouting_report_stream

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


@router.get("/players/{player_id}/report-stream")
def get_player_report_stream(player_id: int, lang: str = Query("en", regex="^(en|es)$")):
    return StreamingResponse(
        generate_scouting_report_stream(player_id, lang),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

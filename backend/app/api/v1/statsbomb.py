import json

from fastapi import APIRouter, Query
import pandas as pd

from app.services import statsbomb

router = APIRouter()


def _serialize(df: pd.DataFrame) -> list:
    return json.loads(df.to_json(orient="records", date_format="iso"))


@router.get("/competitions")
def list_competitions():
    return _serialize(statsbomb.get_competitions())


@router.get("/competitions/{competition_id}/seasons")
def list_seasons(competition_id: int):
    comps = statsbomb.get_competitions()
    seasons = comps[comps["competition_id"] == competition_id][
        ["season_id", "season_name", "match_available"]
    ].drop_duplicates()
    return _serialize(seasons)


@router.get("/matches/{competition_id}/{season_id}")
def list_matches(competition_id: int, season_id: int):
    return _serialize(statsbomb.get_matches(competition_id, season_id))


@router.get("/events/{match_id}")
def get_events(match_id: int):
    events = statsbomb.get_match_events(match_id)
    return _serialize(events)


@router.get("/lineups/{match_id}")
def get_lineups(match_id: int):
    return statsbomb.get_match_lineups(match_id)


@router.get("/players")
def search_players(q: str = Query(default="")):
    return _serialize(statsbomb.search_players(query=q))

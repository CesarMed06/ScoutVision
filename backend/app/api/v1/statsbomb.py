import json

from fastapi import APIRouter, Query
import pandas as pd

from app.services import statsbomb
from app.services.player_images import get_player_photo

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


@router.get("/players/featured")
def get_featured_players():
    df = statsbomb.search_players(limit=10000)
    # Count matches per player and get their info
    player_matches = {}
    player_info = {}
    for _, row in df.iterrows():
        pid = row["player_id"]
        player_matches[pid] = player_matches.get(pid, 0) + 1
        if pid not in player_info:
            player_info[pid] = {
                "player_name": row["player_name"],
                "team": row.get("team", ""),
                "match_id": int(row.get("match_id", 0)),
                "competition": row.get("competition", ""),
                "season": row.get("season", ""),
            }
    # Sort by match count descending, take top 50
    sorted_pids = sorted(player_matches.keys(), key=lambda p: player_matches[p], reverse=True)[:50]
    return [{
        "player_id": int(pid),
        "player_name": player_info[pid]["player_name"],
        "team": player_info[pid]["team"],
        "match_id": player_info[pid]["match_id"],
        "competition": player_info[pid]["competition"],
        "season": player_info[pid]["season"],
    } for pid in sorted_pids]


@router.get("/players/photo")
def get_player_photo_endpoint(player_name: str = Query(...)):
    return get_player_photo(player_name)

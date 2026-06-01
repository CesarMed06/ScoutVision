import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
from statsbombpy import sb

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(name: str) -> Path:
    return DATA_DIR / f"{name}.json"


def _load_cached(name: str):
    path = _cache_path(name)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _save_cache(name: str, data):
    path = _cache_path(name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, default=str)


def get_competitions() -> pd.DataFrame:
    cached = _load_cached("competitions")
    if cached is not None:
        return pd.DataFrame(cached)
    comps = sb.competitions()
    cols = [
        "competition_id",
        "competition_name",
        "country_name",
        "season_name",
        "season_id",
        "match_available_360",
        "match_available",
    ]
    result = comps[cols]
    _save_cache("competitions", json.loads(result.to_json(orient="records")))
    return result


def get_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    cache_name = f"matches_{competition_id}_{season_id}"
    cached = _load_cached(cache_name)
    if cached is not None:
        return pd.DataFrame(cached)
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    cols = [
        "match_id",
        "match_date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "competition_stage",
        "stadium",
    ]
    result = matches[cols]
    _save_cache(cache_name, json.loads(result.to_json(orient="records")))
    return result


@lru_cache(maxsize=128)
def get_match_events(match_id: int) -> pd.DataFrame:
    cache_name = f"events_{match_id}"
    cached = _load_cached(cache_name)
    if cached is not None:
        return pd.DataFrame(cached)
    events = sb.events(match_id=match_id)
    _save_cache(cache_name, json.loads(events.to_json(orient="records")))
    return events


def get_match_lineups(match_id: int) -> list:
    cache_name = f"lineups_{match_id}"
    cached = _load_cached(cache_name)
    if cached is not None:
        return cached
    raw = sb.lineups(match_id=match_id)
    result = []
    for team_name, lineup_df in raw.items():
        players = json.loads(lineup_df.to_json(orient="records"))
        result.append({"team": team_name, "players": players})
    _save_cache(cache_name, result)
    return result


TARGET_LEAGUES = [
    (9, 27),
    (9, 281),
    (2, 27),
    (11, 27),
    (16, 4),
]

EXTRA_MATCHES = [
    3825660,
    3825637,
    3825645,
    3825627,
    3825617,
    267533,
    267576,
    266424,
    3890508,
    3890519,
    3890526,
    3890547,
]



def _build_player_index():
    comps = sb.competitions()
    all_players = []
    for cid, sid in TARGET_LEAGUES:
        comp_row = comps[
            (comps["competition_id"] == cid) & (comps["season_id"] == sid)
        ]
        if len(comp_row) == 0:
            continue
        comp = comp_row.iloc[0]
        matches = sb.matches(competition_id=cid, season_id=sid).head(50)
        mids = list(matches["match_id"].values)
        for mid in EXTRA_MATCHES:
            if mid not in mids:
                mids.append(mid)
        for mid in mids:
            raw = sb.lineups(match_id=mid)
            for team_name, lineup_df in raw.items():
                for _, p in lineup_df.iterrows():
                    all_players.append(
                        {
                            "player_id": p["player_id"],
                            "player_name": p["player_name"],
                            "team": team_name,
                            "match_id": mid,
                            "competition": comp["competition_name"],
                            "season": comp["season_name"],
                        }
                    )
    df = pd.DataFrame(all_players)
    _save_cache("players_index", json.loads(df.to_json(orient="records")))
    return df


def search_players(query: str = "", limit: int = 100) -> pd.DataFrame:
    cached = _load_cached("players_index")
    if cached is not None:
        df = pd.DataFrame(cached)
    else:
        df = _build_player_index()
    if query:
        q = query.replace("ue", "ü").replace("oe", "ö").replace("ae", "ä")
        df = df[df["player_name"].str.contains(q, case=False, na=False)]
    return df.head(limit)

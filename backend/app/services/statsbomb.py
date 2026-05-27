import json
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


def search_players(query: str = "", limit: int = 100) -> pd.DataFrame:
    cache_name = "players_index"
    cached = _load_cached(cache_name)
    if cached is not None:
        df = pd.DataFrame(cached)
    else:
        comps = sb.competitions().head(5)
        all_players = []
        count = 0
        for _, comp in comps.iterrows():
            if count >= 1000:
                break
            matches = sb.matches(
                competition_id=comp["competition_id"],
                season_id=comp["season_id"],
            ).head(10)
            for _, match in matches.iterrows():
                if count >= 1000:
                    break
                raw = sb.lineups(match_id=match["match_id"])
                for team_name, lineup_df in raw.items():
                    for _, p in lineup_df.iterrows():
                        all_players.append(
                            {
                                "player_id": p["player_id"],
                                "player_name": p["player_name"],
                                "team": team_name,
                                "match_id": match["match_id"],
                                "competition": comp["competition_name"],
                                "season": comp["season_name"],
                            }
                        )
                        count += 1
                        if count >= 1000:
                            break
        df = pd.DataFrame(all_players)
        _save_cache(cache_name, json.loads(df.to_json(orient="records")))
    if query:
        df = df[df["player_name"].str.contains(query, case=False, na=False)]
    return df.head(limit)

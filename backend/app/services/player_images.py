import json
import logging
from pathlib import Path
from urllib.request import urlopen

from app.core.config import settings

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = DATA_DIR / "player_images_cache.json"

SPORTSDB_URL = "https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p="


def _load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f)


def _sportsdb_search(name: str) -> str | None:
    """Search TheSportsDB for a player by name. Returns thumbnail URL or None."""
    try:
        url = SPORTSDB_URL + name.replace(" ", "%20")
        with urlopen(url, timeout=5) as res:
            data = json.loads(res.read().decode())
        players = data.get("player", [])
        if players:
            p = players[0]
            return p.get("strThumb") or p.get("strCutout") or p.get("strPNG") or p.get("strRender")
        return None
    except Exception as e:
        logger.warning(f"TheSportsDB error for '{name}': {e}")
        return None


def _search_name_variations(full_name: str) -> str | None:
    """Try multiple name variations to find a photo on TheSportsDB."""
    # First try the full name
    result = _sportsdb_search(full_name)
    if result:
        return result

    # Try first + last name
    parts = full_name.split()
    if len(parts) >= 3:
        # Try first_name + last_name
        short_name = f"{parts[0]} {parts[-1]}"
        result = _sportsdb_search(short_name)
        if result:
            return result

    # Try just the last name (for famous players)
    if len(parts) >= 2:
        result = _sportsdb_search(parts[-1])
        if result:
            return result

    return None


def get_player_image(player_name: str) -> str | None:
    cache = _load_cache()
    if player_name in cache:
        return cache[player_name].get("thumb")

    thumb = _search_name_variations(player_name)

    cache[player_name] = {"thumb": thumb}
    _save_cache(cache)
    return thumb


def get_player_photo(player_name: str) -> dict:
    thumb = get_player_image(player_name)
    return {
        "player_name": player_name,
        "photo_url": thumb,
    }

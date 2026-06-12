import json
import logging
import re
import threading
import unicodedata
import urllib.parse
from pathlib import Path
from urllib.request import urlopen

from app.core.config import settings

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = DATA_DIR / "player_images_cache.json"
CACHE_LOCK = threading.Lock()

SPORTSDB_URL = "https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p="


def _load_cache():
    with CACHE_LOCK:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Photo cache corrupted, resetting...")
                try:
                    CACHE_FILE.unlink(missing_ok=True)
                except OSError:
                    pass
        return {}


def _save_cache(cache):
    with CACHE_LOCK:
        tmp = CACHE_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f)
        try:
            tmp.replace(CACHE_FILE)
        except OSError:
            tmp.unlink(missing_ok=True)


def _strip_accents(name: str) -> str:
    """Remove diacritics/accents from a name (e.g. Suárez -> Suarez)."""
    nfkd = unicodedata.normalize("NFKD", name)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


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
    # Generate name variations to try
    names_to_try = [full_name]
    parts = full_name.split()

    # Add first + last name (skip middle names)
    if len(parts) >= 3:
        names_to_try.append(f"{parts[0]} {parts[-1]}")
        names_to_try.append(f"{parts[0]} {parts[1]}")

    # Add just first name + last name (2-part version)
    if len(parts) >= 2:
        names_to_try.append(f"{parts[0]} {parts[-1]}")

    # Add accented versions for each name tried
    all_variants = []
    for n in names_to_try:
        all_variants.append(n)
        stripped = _strip_accents(n)
        if stripped != n:
            all_variants.append(stripped)

    # Deduplicate while preserving order
    seen = set()
    unique_variants = []
    for n in all_variants:
        if n not in seen:
            seen.add(n)
            unique_variants.append(n)

    for name in unique_variants:
        result = _sportsdb_search(name)
        if result:
            return result

    return None


def _wikipedia_search(name: str) -> str | None:
    try:
        search_url = (
            "https://en.wikipedia.org/w/api.php?action=query&list=search"
            f"&srsearch={urllib.parse.quote(name + ' footballer')}"
            "&format=json&srlimit=1"
        )
        with urlopen(search_url, timeout=5) as res:
            data = json.loads(res.read().decode())
        results = data.get("query", {}).get("search", [])
        if not results:
            return None
        title = urllib.parse.quote(results[0]["title"])
        img_url = (
            f"https://en.wikipedia.org/w/api.php?action=query&titles={title}"
            "&prop=pageimages&format=json&pithumbsize=200"
        )
        with urlopen(img_url, timeout=5) as res:
            data = json.loads(res.read().decode())
        for page in data.get("query", {}).get("pages", {}).values():
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
        return None
    except Exception as e:
        logger.warning(f"Wikipedia error for '{name}': {e}")
        return None


def _ui_avatar_url(player_name: str) -> str:
    initials = "+".join([p[0].upper() for p in player_name.split()[:2]])
    return f"https://ui-avatars.com/api/?name={initials}&background=064e3b&color=34d399&size=200&bold=true&font-size=0.4"


def get_player_image(player_name: str) -> str | None:
    cache = _load_cache()
    if player_name in cache and cache[player_name].get("thumb"):
        return cache[player_name]["thumb"]

    thumb = _search_name_variations(player_name)
    if not thumb:
        thumb = _wikipedia_search(player_name)
    if not thumb:
        thumb = _ui_avatar_url(player_name)

    cache[player_name] = {"thumb": thumb}
    _save_cache(cache)
    return thumb


def get_player_photo(player_name: str) -> dict:
    thumb = get_player_image(player_name)
    return {
        "player_name": player_name,
        "photo_url": thumb,
    }

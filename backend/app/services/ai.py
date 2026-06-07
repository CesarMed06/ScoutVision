import logging
import time

from groq import Groq

from app.core.config import settings
from app.services.metrics import get_player_metrics_across_matches

logger = logging.getLogger(__name__)

_report_cache: dict[tuple, tuple[str, float]] = {}
REPORT_CACHE_TTL = 3600


def _build_report_prompt(player_info: dict, totals: dict, match_details: list[dict], lang: str) -> str:
    name = player_info["player_name"]
    team = player_info.get("team", "Unknown")
    competition = player_info.get("competition", "Unknown")

    lines = []
    lines.append(f"Player: {name}")
    lines.append(f"Team: {team}")
    lines.append(f"Competition: {competition}")
    lines.append(f"Matches analyzed: {totals.get('matches', 0)}")
    lines.append(f"Total minutes: {totals.get('minutes', 0)}")
    lines.append("")

    metric_labels = {
        "goals": "Goals",
        "xg": "xG",
        "xg_per_90": "xG per 90",
        "assists": "Assists",
        "xa": "xA",
        "xa_per_90": "xA per 90",
        "shots": "Shots",
        "shots_on_target": "Shots on target",
        "shot_accuracy": "Shot accuracy (%)",
        "passes": "Passes",
        "pass_completion_pct": "Pass completion (%)",
        "key_passes": "Key passes",
        "progressive_passes": "Progressive passes",
        "passes_into_final_third": "Passes into final third",
        "crosses": "Crosses",
        "through_balls": "Through balls",
        "dribbles": "Dribbles",
        "dribble_success_pct": "Dribble success (%)",
        "progressive_carries": "Progressive carries",
        "duel_success_pct": "Duel success (%)",
        "tackles": "Tackles",
        "tackle_success_pct": "Tackle success (%)",
        "aerial_success_pct": "Aerial success (%)",
        "pressures": "Pressures",
        "interceptions": "Interceptions",
        "clearances": "Clearances",
        "blocks": "Blocks",
        "fouls_committed": "Fouls committed",
        "fouls_won": "Fouls won",
    }

    for key, label in metric_labels.items():
        val = totals.get(key)
        if val is not None:
            lines.append(f"- {label}: {val}")

    metrics_text = "\n".join(lines)

    if lang == "es":
        return f"""Eres un ojeador profesional de fútbol con 20 años de experiencia en scoutíng de élite. Has trabajado para clubs como Barcelona, Bayern Múnich y Ajax. Eres conocido por tus informes detallados, directos y sin florituras.

A continuación tienes las métricas de rendimiento de un jugador. Genera un informe de scouting profesional en ESPAÑOL con el siguiente formato:

---
SCOUTING REPORT: {name}
---

PERFIL DEL JUGADOR
[2-3 frases describiendo el perfil general del jugador basado en sus números]

FORTALEZAS
- [5-7 puntos concretos basados en las métricas, con valores específicos]

ÁREAS DE MEJORA
- [3-5 áreas donde el jugador podría mejorar]

VALORACIÓN ESTADÍSTICA
[2-3 frases con análisis estadístico comparativo sobre rendimiento]

NOTA DE SCOUTING (1-10)
[X.X/10]

VEREDICTO FINAL
[Recomendación final clara: fichar / seguir / descartar, con razones concretas]

DATOS ANALIZADOS:
{metrics_text}

IMPORTANTE: Sé directo, sin halagos vacíos. Si los números son malos, dilo. Si son buenos, reconócelo. Usa un tono profesional pero natural, como un ojeador hablando con un director deportivo. NO uses frases genéricas de ChatGPT. Cada frase debe estar respaldada por un dato concreto de las métricas."""

    return f"""You are a professional football scout with 20 years of elite scouting experience. You have worked for clubs like Barcelona, Bayern Munich, and Ajax. You are known for your detailed, direct, no-nonsense reports.

Below are the performance metrics for a player. Generate a professional scouting report with the following format:

---
SCOUTING REPORT: {name}
---

PLAYER PROFILE
[2-3 sentences describing the player's overall profile based on their numbers]

STRENGTHS
- [5-7 concrete points backed by specific metric values]

AREAS FOR IMPROVEMENT
- [3-5 areas where the player could improve]

STATISTICAL ASSESSMENT
[2-3 sentences of comparative statistical analysis]

SCOUTING GRADE (1-10)
[X.X/10]

FINAL VERDICT
[Clear final recommendation: sign / monitor / pass, with concrete reasons]

DATA ANALYZED:
{metrics_text}

IMPORTANT: Be direct, no empty praise. If the numbers are bad, say it. If they're good, acknowledge it. Use a professional but natural tone, like a scout talking to a sporting director. Do NOT use generic ChatGPT phrases. Every sentence must be backed by a specific data point from the metrics."""


def generate_scouting_report(player_id: int, lang: str = "en") -> str:
    key = (player_id, lang)
    now = time.time()
    cached = _report_cache.get(key)
    if cached and now - cached[1] < REPORT_CACHE_TTL:
        return cached[0]
    if not settings.groq_api_key:
        return "GROQ_API_KEY not configured. Add it to your .env file."

    metrics_data = get_player_metrics_across_matches(player_id)
    if not metrics_data:
        return f"No match data found for player ID {player_id}."

    first = metrics_data[0]
    player_info = {
        "player_id": player_id,
        "player_name": first.get("player", "Unknown"),
        "team": first.get("team", ""),
        "competition": first.get("competition", ""),
        "season": first.get("season", ""),
    }

    totals = {}
    skip_keys = {"player", "match_id", "team", "competition", "season"}
    for key in first:
        if key in skip_keys:
            continue
        if key.endswith("_pct") or key.endswith("_per_90"):
            continue
        totals[key] = sum(m.get(key, 0) or 0 for m in metrics_data)

    totals["matches"] = len(metrics_data)
    total_minutes = totals.get("minutes", 0) or 1
    p90 = lambda v: round(v / total_minutes * 90, 2)

    totals["xg"] = round(totals.get("xg", 0), 2)
    totals["xa"] = round(totals.get("xa", 0), 2)
    totals["goals_per_90"] = p90(totals.get("goals", 0))
    totals["xg_per_90"] = p90(totals.get("xg", 0))
    totals["xa_per_90"] = p90(totals.get("xa", 0))
    totals["key_passes_per_90"] = p90(totals.get("key_passes", 0))
    totals["shots_per_90"] = p90(totals.get("shots", 0))
    totals["passes_per_90"] = p90(totals.get("passes", 0))
    totals["dribbles_per_90"] = p90(totals.get("dribbles", 0))
    totals["tackles_per_90"] = p90(totals.get("tackles", 0))
    totals["pressures_per_90"] = p90(totals.get("pressures", 0))

    shots = totals.get("shots", 0) or 1
    totals["shot_accuracy"] = round(totals.get("shots_on_target", 0) / shots * 100, 1)
    passes = totals.get("passes", 0) or 1
    totals["pass_completion_pct"] = round(totals.get("passes_completed", 0) / passes * 100, 1)
    dribbles = totals.get("dribbles", 0) or 1
    totals["dribble_success_pct"] = round(totals.get("dribbles_completed", 0) / dribbles * 100, 1)
    duels = totals.get("duels", 0) or 1
    totals["duel_success_pct"] = round(totals.get("duels_won", 0) / duels * 100, 1)
    tackles = totals.get("tackles", 0) or 1
    totals["tackle_success_pct"] = round(totals.get("tackles_won", 0) / tackles * 100, 1)
    aerials = totals.get("aerial_duels", 0) or 1
    totals["aerial_success_pct"] = round(totals.get("aerial_duels_won", 0) / aerials * 100, 1)

    prompt = _build_report_prompt(player_info, totals, metrics_data, lang)

    try:
        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional football scout. Be direct, specific, and data-driven. Never use generic filler phrases.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        report = response.choices[0].message.content
        _report_cache[key] = (report, now)
        return report
    except Exception as e:
        logger.error(f"Groq API error for player {player_id}: {e}")
        return f"GROQ_API_ERROR: {str(e)}"

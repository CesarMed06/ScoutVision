import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mplsoccer import Pitch, Radar
import pandas as pd

from app.services.statsbomb import get_match_events, search_players
from app.services.metrics import get_player_metrics_across_matches


def _find_player_name(player_id):
    rows = search_players(limit=10000)
    rows = rows[rows["player_id"] == player_id]
    if len(rows) == 0:
        return None
    return rows.iloc[0]["player_name"]


def _get_player_events(player_id, match_id):
    player_name = _find_player_name(player_id)
    if player_name is None:
        return None, None, None
    events = get_match_events(match_id)
    if len(events) == 0:
        return None, None, None
    if player_name in events["player"].values:
        matched = player_name
    else:
        matched = None
        for p in events["player"].dropna().unique():
            if player_name in p or p in player_name:
                matched = p
                break
        if matched is None:
            return None, None, None
    return events[events["player"] == matched], matched, events


def player_heatmap(player_id, match_id):
    player_events, _, _ = _get_player_events(player_id, match_id)
    if player_events is None:
        return None
    locs = player_events["location"].dropna()
    if len(locs) < 5:
        return None
    x = [l[0] for l in locs]
    y = [l[1] for l in locs]
    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc")
    fig, ax = pitch.draw(figsize=(10, 7))
    pitch.kdeplot(x, y, ax=ax, fill=True, cmap="hot", n_levels=10, alpha=0.8)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#22312b")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def player_passes(player_id, match_id):
    player_events, player_name, _ = _get_player_events(player_id, match_id)
    if player_events is None:
        return None
    passes = player_events[player_events["type"] == "Pass"]
    if len(passes) == 0:
        return None
    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc")
    fig, ax = pitch.draw(figsize=(10, 7))
    for _, p in passes.iterrows():
        loc = p.get("location")
        end = p.get("pass_end_location")
        if not isinstance(loc, (list, tuple)) or not isinstance(end, (list, tuple)):
            continue
        outcome = p.get("pass_outcome")
        color = "#00ff87" if pd.isna(outcome) else "#ff6b6b"
        alpha = 0.5
        lw = 1.2
        pitch.lines(loc[0], loc[1], end[0], end[1], ax=ax, color=color, alpha=alpha, lw=lw, zorder=2)
    ax.set_title(f"{player_name}\nPass Map ({len(passes)} passes)", color="white", fontsize=14, pad=15)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#22312b")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def player_shots(player_id, match_id):
    player_events, player_name, _ = _get_player_events(player_id, match_id)
    if player_events is None:
        return None
    shots = player_events[player_events["type"] == "Shot"]
    if len(shots) == 0:
        return None
    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc", goal_type="box")
    fig, ax = pitch.draw(figsize=(10, 7))
    colors = {"Goal": "#00ff87", "Saved": "#ffd93d", "Off T": "#ff6b6b",
              "Post": "#ffd93d", "Blocked": "#6c757d", "Wayward": "#6c757d"}
    for _, s in shots.iterrows():
        loc = s.get("location")
        if not isinstance(loc, (list, tuple)):
            continue
        outcome = s.get("shot_outcome", "")
        c = colors.get(outcome, "#6c757d")
        size = 130 if outcome == "Goal" else 90
        pitch.scatter(loc[0], loc[1], ax=ax, s=size, color=c, edgecolor="white", linewidth=1, alpha=0.85, zorder=3)
    ax.set_title(f"{player_name}\nShot Map ({len(shots)} shots)", color="white", fontsize=14, pad=15)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#22312b")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def player_radar(player_id):
    matches = get_player_metrics_across_matches(player_id)
    if not matches:
        return None
    totals = {}
    for m in matches:
        for k, v in m.items():
            if k in ("player", "match_id", "team", "competition", "season"):
                continue
            totals[k] = totals.get(k, 0) + (v or 0)
    total_minutes = totals.get("minutes", 0) or 1
    p90 = lambda v: round(v / total_minutes * 90, 2)

    metric_keys = ["xg", "xa", "key_passes", "progressive_passes", "dribbles", "tackles", "pressures"]
    params = ["xG", "xA", "Key\nPasses", "Prog.\nPasses", "Dribbles", "Tackles", "Pressures"]
    values = [round(p90(totals.get(k, 0)), 2) for k in metric_keys]

    max_ranges = [1.5, 1.0, 6, 15, 8, 5, 25]
    min_ranges = [0] * len(params)
    radar = Radar(params, min_ranges, max_ranges, round_int=[False] * len(params))

    fig, ax = radar.setup_axis(figsize=(8, 8), facecolor="#1a1a2e")
    fig.patch.set_facecolor("#1a1a2e")

    radar.draw_circles(ax=ax, inner=True, facecolor="#2d2d44", edgecolor="#4a4a6a", linewidth=0.5)
    radar.draw_radar_solid(values, ax=ax, kwargs={"facecolor": "#00ff87", "alpha": 0.7, "edgecolor": "#ffffff", "linewidth": 1.5})
    radar.draw_range_labels(ax=ax, color="#aaaaaa", fontsize=7)
    radar.draw_param_labels(ax=ax, color="white", fontsize=9)

    player_name = matches[0]["player"]
    ax.set_title(f"{player_name}\nScout Radar (per 90')", color="white", fontsize=14, pad=25)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def match_heatmap(match_id):
    events = get_match_events(match_id)
    if len(events) == 0:
        return None
    locs = events["location"].dropna()
    if len(locs) < 10:
        return None
    x = [l[0] for l in locs]
    y = [l[1] for l in locs]
    pitch = Pitch(pitch_type="statsbomb", pitch_color="#22312b", line_color="#c7d5cc")
    fig, ax = pitch.draw(figsize=(10, 7))
    pitch.kdeplot(x, y, ax=ax, fill=True, cmap="viridis", n_levels=10, alpha=0.7)
    ax.set_title(f"Match {match_id}\nAll Events Heatmap", color="white", fontsize=14, pad=15)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#22312b")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

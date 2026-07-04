<div align="center">
  <img src="https://github.com/CesarMed06/ScoutVision/actions/workflows/ci.yml/badge.svg" alt="CI" />
  <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status" />
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/python-3.12+-blue?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/react-18.x-61DAFB?logo=react" alt="React" />
  <img src="https://img.shields.io/badge/llama-3.3-FF6F00?logo=meta" alt="Llama" />
</div>

<br />

<p align="center">
  <img src="docs/banner.jpeg" alt="ScoutVision AI Banner" width="1200" />
</p>

# ScoutVision AI ⚽🧠

ScoutVision AI is a football scouting platform built around open match data, advanced metrics, tactical visualizations, and AI-generated reports.

It takes raw StatsBomb data and turns it into something closer to a real scouting workflow: player search, profile analysis, comparisons, similarity discovery, match-level visualizations, and narrative reports powered by Llama 3 through Groq.

## Overview

The idea behind ScoutVision is simple: combine football data and AI in a way that feels useful, practical, and accessible.

Instead of building a generic stats dashboard, the project focuses on a scouting perspective:
- Find players quickly.
- Understand how they perform across matches.
- Compare profiles side by side.
- Visualize actions on the pitch.
- Generate structured scouting reports in English or Spanish.

## Highlights

- Real StatsBomb Open Data ingestion for matches, events, and lineups
- Advanced player metrics including xG, xA, progressive actions, pressures, duels, and efficiency stats
- Tactical visualizations such as heatmaps, pass maps, and shot maps
- AI scouting reports generated with Llama 3.3 70B via Groq
- Similar player discovery with vector-based comparisons
- Interactive scouting dashboard built with React, Vite, and Tailwind
- 100% free stack using open data and free-tier compatible services

## Product Demo

Add screenshots or a short GIF here once the final UI assets are ready.

```md
<p align="center">
  <img src="docs/demo.gif" alt="ScoutVision Demo" width="900" />
</p>
```

Recommended captures:
- Home page
- Players list
- Player profile
- Compare page
- Scout filters
- AI report panel

## Architecture

```text
┌──────────────┐     ┌──────────────────┐     ┌────────────────┐
│  StatsBomb   │────▶│  Python/FastAPI  │────▶│  React + Vite  │
│  Open Data   │     │  + Llama 3/Groq  │     │  + Tailwind    │
└──────────────┘     └──────────────────┘     └────────────────┘
                          │                           │
                    ┌─────┴──────┐              ┌─────┴──────┐
                    │  Pandas    │              │  Recharts  │
                    │  mplsoccer │              │  Lucide    │
                    │  Groq SDK  │              │  Dark Mode │
                    └────────────┘              └────────────┘
```

## Core Features

### Player search and profiles
Search players from the StatsBomb dataset and open detailed profiles with aggregated match data, efficiency metrics, and per-90 stats.

### AI scouting reports
Generate structured reports in English or Spanish with strengths, improvement areas, statistical assessment, and a final scouting verdict.

### Similar player discovery
Find players with comparable profiles using vector-based similarity across key performance metrics, with support for position-aware filtering.

### Match visualizations
Inspect individual matches through pitch-based visualizations such as heatmaps, pass maps, and shot maps.

### Comparison tools
Compare two players side by side to quickly understand stylistic and statistical differences.

### Scout mode
Filter the player pool using thresholds such as xG per 90, xA per 90, key passes, tackles, pass accuracy, dribble success, aerial success, and pressures.

## Available Metrics

| Category | Metrics |
|---|---|
| Attacking | Goals, shots, shots on target, xG, assists, xA, shot accuracy |
| Passing | Passes, pass completion, key passes, progressive passes, passes into final third, crosses, through balls |
| Ball carrying | Dribbles, dribbles completed, progressive carries |
| Defending | Pressures, tackles, tackle success, interceptions, clearances, blocks |
| Duel play | Duels, duel success, aerial duels, aerial success |
| Derived stats | Per-90 metrics, percentage efficiency metrics, similarity vectors |

## Tech Stack

| Layer | Technology |
|---|---|
| Data | StatsBomb Open Data |
| Backend | Python, FastAPI, Pandas, Scikit-learn |
| AI | Llama 3.3 70B via Groq API |
| Visualizations | mplsoccer, Matplotlib, Recharts |
| Frontend | React, Vite, Tailwind CSS, TypeScript, Lucide |
| CI | GitHub Actions |
| Deployment | Render, Vercel |

## Project Structure

```text
ScoutVision/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   └── visualizations/
│   ├── data/
│   └── tests/
├── docs/
├── frontend/
│   ├── public/
│   └── src/
└── docker-compose.yml
```

## Quick Start

### Requirements

- Python 3.12+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

On Windows:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Set your `GROQ_API_KEY` inside `.env` before generating AI reports.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

## Environment Variables

Backend `.env`:

```env
GROQ_API_KEY=your_key_here
```

Add any extra variables here if the project grows later.

## Quality and Tooling

- Automated CI with GitHub Actions
- Backend test suite with pytest
- Rate limiting enabled in the API
- Health check endpoint available at `/health`
- Vector database persisted locally for faster similarity startup
- Error boundary and defensive UI states on the frontend

## Why this project

ScoutVision was built as a portfolio project around two interests: football and AI.

The goal was not just to display statistics, but to build a small end-to-end product with a real backend, real data processing, practical frontend UX, and AI features that feel integrated into the workflow instead of bolted on.

## Roadmap

Planned ideas that could be explored later:
- Team-level scouting views
- More competitions and datasets
- Exportable PDF scouting reports
- Player role classification
- Authentication and saved shortlists

## License

MIT

---

<p align="center">
  Built with care for football, data, and product thinking
</p>
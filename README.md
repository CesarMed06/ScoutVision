<div align="center">
  <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status" />
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/python-3.12+-blue?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/react-18.x-61DAFB?logo=react" alt="React" />
  <img src="https://img.shields.io/badge/llama-3.3-FF6F00?logo=meta" alt="Llama" />
</div>

<br />

<p align="center">
  <img src="https://via.placeholder.com/1200x400/1a1a2e/00ff88?text=ScoutVision+AI" alt="ScoutVision AI Banner" />
</p>

# ScoutVision AI ⚽🧠

**AI-powered football scouting engine** — ingests real match data from StatsBomb Open Data, computes advanced performance metrics, generates tactical visualizations, and produces AI-driven scouting reports using Llama 3 via Groq API.

Inspired by the data-driven approach that clubs like Schalke 04, Brighton, and Brentford use to find hidden talent.

## ✨ Features

- **Data Pipeline** — Automatically ingests and parses StatsBomb Open Data (matches, events, lineups)
- **Metrics Engine** — Calculates xG, xA, progressive passes, pressures, duel success rate, and more
- **Tactical Visualizations** — Heatmaps, pitch plots, and passing networks rendered with mplsoccer
- **AI Scouting Reports** — Narrative reports in English or Spanish powered by Llama 3.3 70B
- **Interactive Dashboard** — Search players, compare stats, view visualizations, and read AI analysis
- **100% Free** — No paid APIs, all open-source, deployable on free tiers

## 🏗️ Architecture

```
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

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- [Groq API key](https://console.groq.com) (free tier, 14,400 requests/day)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and start exploring.

## 📊 Available Metrics

| Category | Metrics |
|---|---|
| Attacking | xG, shots, goals, shot accuracy, key passes, xA, assists |
| Passing | Pass completion, progressive passes, through balls, crosses |
| Defending | Pressures, tackles, interceptions, clearances, duel win rate |
| Physical | Distance covered, sprints, aerial duels |
| Tactical | Pass network centrality, heatmap density, formation fit |

## 🗺️ Roadmap

- [x] Project setup & architecture
- [ ] Data ingestion pipeline (StatsBomb)
- [ ] Player metrics engine & API
- [ ] Tactical visualizations
- [ ] AI scouting reports (Groq + Llama 3)
- [ ] Interactive dashboard
- [ ] Deployment & polish

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data | StatsBomb Open Data |
| Backend | Python, FastAPI, Pandas, Scikit-learn |
| AI | Llama 3.3 70B via Groq API |
| Visuals | mplsoccer, Matplotlib, Recharts |
| Frontend | React, Vite, Tailwind CSS, Lucide |
| Deployment | Render (backend), Vercel (frontend) |

## 📝 License

MIT

---

<p align="center">
  Built with ❤️ for football and data science
</p>

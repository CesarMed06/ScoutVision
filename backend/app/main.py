import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.statsbomb import router as statsbomb_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.visualizations import router as viz_router
from app.api.v1.ai import router as ai_router
from app.api.v1.similarity import router as similarity_router

logger = logging.getLogger(__name__)


def _prewarm_cache():
    """Pre-compute metrics for top players at startup so caches are warm."""
    from app.services.statsbomb import search_players
    from app.services.metrics import get_player_metrics_across_matches
    
    logger.info("Pre-warming metric cache for top 50 players...")
    df = search_players(limit=10000)
    seen = set()
    pids = []
    for _, row in df.iterrows():
        pid = row["player_id"]
        if pid not in seen:
            seen.add(pid)
            pids.append(pid)
    count = 0
    for pid in pids[:50]:
        try:
            get_player_metrics_across_matches(int(pid))
            count += 1
        except Exception as e:
            logger.warning(f"Pre-warm failed for pid {pid}: {e}")
    logger.info(f"Pre-warming complete: {count}/{min(50, len(pids))} players cached")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: pre-warm caches in background thread
    thread = threading.Thread(target=_prewarm_cache, daemon=True)
    thread.start()
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="ScoutVision AI",
    description="AI-powered football scouting engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(statsbomb_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1/metrics")
app.include_router(viz_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(similarity_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

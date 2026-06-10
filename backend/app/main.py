import logging
import threading
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.statsbomb import router as statsbomb_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.visualizations import router as viz_router
from app.api.v1.ai import router as ai_router
from app.api.v1.similarity import router as similarity_router
from app.api.v1.scout import router as scout_router

logger = logging.getLogger(__name__)


def _prewarm_cache():
    """Pre-compute vector DB at startup for instant KNN similarity."""
    from app.services.similarity import init_vector_db, VECTOR_DB

    logger.info("Building vector database for KNN similarity...")
    try:
        init_vector_db(max_players=2000)
        logger.info(f"Vector DB ready: {len(VECTOR_DB)} players indexed")
    except Exception as e:
        logger.error(f"Vector DB init failed: {e}")


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
app.include_router(scout_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    from app.services.similarity import VECTOR_DB, _VECTOR_DB_INITIALIZED
    return {
        "status": "ok",
        "version": "0.1.0",
        "vector_db_initialized": _VECTOR_DB_INITIALIZED,
        "vector_db_size": len(VECTOR_DB) if _VECTOR_DB_INITIALIZED else 0,
    }

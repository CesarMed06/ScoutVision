import logging
import threading
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import APP_VERSION, settings
from app.api.v1.statsbomb import router as statsbomb_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.visualizations import router as viz_router
from app.api.v1.ai import router as ai_router
from app.api.v1.similarity import router as similarity_router
from app.api.v1.scout import router as scout_router

logger = logging.getLogger(__name__)


def _prewarm_cache():
    import app.services.similarity as sim

    logger.info("Building vector database for KNN similarity...")
    try:
        sim.init_vector_db(max_players=2000)
        logger.info(f"Vector DB ready: {len(sim.VECTOR_DB)} players indexed")
    except Exception as e:
        logger.error(f"Vector DB init failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: pre-warm caches in background thread
    thread = threading.Thread(target=_prewarm_cache, daemon=True)
    thread.start()
    yield
    # Shutdown: nothing to clean up


limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

app = FastAPI(
    title="ScoutVision AI",
    description="AI-powered football scouting engine",
    version=APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    import app.services.similarity as sim
    return {
        "status": "ok",
        "version": APP_VERSION,
        "vector_db_initialized": sim._VECTOR_DB_INITIALIZED,
        "vector_db_size": len(sim.VECTOR_DB) if sim._VECTOR_DB_INITIALIZED else 0,
    }

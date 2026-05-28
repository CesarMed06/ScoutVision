from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.statsbomb import router as statsbomb_router
from app.api.v1.metrics import router as metrics_router

app = FastAPI(
    title="ScoutVision AI",
    description="AI-powered football scouting engine",
    version="0.1.0",
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


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

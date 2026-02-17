"""
FastAPI application entry point.
Configures CORS, includes all routers, creates tables, and seeds data on startup.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.profile import UserProfile
from app.models.area import Area
from app.models.infrastructure import InfrastructureData
from app.routers import auth, profile, areas, infrastructure, scoring, market
from app.seed import seed_areas

# ─── Logging setup ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables and seed data. Shutdown: cleanup."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Seeding predefined areas...")
    db = SessionLocal()
    try:
        seed_areas(db)
    finally:
        db.close()

    logger.info("Application startup complete.")
    yield
    logger.info("Application shutting down.")


# ─── FastAPI app ───
app = FastAPI(
    title="Avenir – Lifestyle Scoring API",
    description="AI-powered lifestyle scoring engine for Hyderabad neighborhoods",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS middleware (allow frontend at localhost:5173 / 8080) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Include routers ───
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(areas.router)
app.include_router(infrastructure.router)
app.include_router(scoring.router)
app.include_router(market.router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "avenir-lifestyle-scoring-api", "version": "1.0.0"}

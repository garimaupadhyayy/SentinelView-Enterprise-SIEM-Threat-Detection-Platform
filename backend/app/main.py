import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, auth, dashboard, events, reports, rules, threat_intel, websocket
from app.core.config import settings
from app.core.db import Base, SessionLocal, engine
from app.services.rule_seeder import seed_builtin_rules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinelview")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist yet, then seed the built-in
    # detection rules. In a production setup you'd use Alembic migrations
    # instead of create_all, but this keeps first-run setup to zero manual
    # steps for a self-hosted portfolio deployment.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_builtin_rules(db)
        logger.info("Built-in detection rules seeded.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="SentinelView API",
    description="Self-hosted SIEM log aggregation and threat correlation platform.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(events.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
app.include_router(rules.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(threat_intel.router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket.router)  # ws paths are not versioned


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}

"""Unified single-service entrypoint for SnapStudy AI (Feature D1).

Combines:
1. Telegram Bot (polling in async lifespan with drop_pending_updates)
2. FastAPI Portal API routes (/api/*)
3. React SPA static file serving (web/dist with SPA fallback)
4. Fast health check (/healthz) returning 200 without touching DB or AI
"""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import ROOT_DIR, settings
from app.db import init_db
from app.logging_setup import setup_logging
from app.main import build_application
from portal.routes import router as api_router

logger = logging.getLogger(__name__)

WEB_DIST_DIR = ROOT_DIR / "web" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan: DB init, bot startup & shutdown."""
    setup_logging(settings.LOG_LEVEL)
    logger.info("Initializing SnapStudy database at %s", settings.DATABASE_PATH)
    init_db(settings.DATABASE_PATH)

    telegram_app = None
    if settings.TELEGRAM_TOKEN:
        try:
            logger.info("Starting Telegram bot polling in lifespan...")
            telegram_app = build_application()
            await telegram_app.initialize()
            await telegram_app.start()
            await telegram_app.updater.start_polling(drop_pending_updates=True)
            logger.info("Telegram bot polling started successfully.")
        except Exception as e:
            logger.error("Failed to start Telegram bot polling in lifespan: %s", e, exc_info=True)
    else:
        logger.warning("TELEGRAM_TOKEN not set; skipping Telegram bot polling.")

    yield

    # Clean shutdown of Telegram bot
    if telegram_app is not None:
        logger.info("Stopping Telegram bot...")
        try:
            if telegram_app.updater and telegram_app.updater.running:
                await telegram_app.updater.stop()
            await telegram_app.stop()
            await telegram_app.shutdown()
            logger.info("Telegram bot cleanly stopped.")
        except Exception as e:
            logger.warning("Error during Telegram bot shutdown: %s", e)


def create_app() -> FastAPI:
    """Create unified FastAPI app."""
    app = FastAPI(title="SnapStudy AI", lifespan=lifespan, docs_url=None, redoc_url=None)

    # CORS support for Vercel frontends and local dev
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global unhandled exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        logger.error("Unhandled error processing %s: %s", request.url.path, exc, exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "internal_error"})

    # Health check endpoint returning 200 without touching DB or AI
    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    # Include portal API routes (/api/*)
    app.include_router(api_router)

    # Static assets and SPA fallback
    if WEB_DIST_DIR.is_dir() and (WEB_DIST_DIR / "index.html").is_file():
        assets_dir = WEB_DIST_DIR / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            if full_path == "healthz" or full_path == "api" or full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="not_found")
            file_path = WEB_DIST_DIR / full_path
            if full_path and file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(WEB_DIST_DIR / "index.html")
    else:
        @app.get("/{full_path:path}")
        async def ui_not_built(full_path: str):
            if full_path == "healthz" or full_path == "api" or full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="not_found")
            return HTMLResponse(
                "<!DOCTYPE html><html><head><title>SnapStudy Portal</title></head>"
                "<body style='font-family:sans-serif;padding:2rem;text-align:center;'>"
                "<h2>Portal UI is not built.</h2>"
                "<p>Run: <code>cd web &amp;&amp; npm ci &amp;&amp; npm run build</code></p>"
                "</body></html>"
            )

    return app


app = create_app()


def main() -> None:
    """Entry point when running directly with python server.py."""
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, access_log=False)


if __name__ == "__main__":
    main()

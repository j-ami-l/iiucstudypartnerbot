"""FastAPI application factory, static SPA mount, and entry point for SnapStudy Portal."""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import ROOT_DIR, settings
from app.db import init_db
from app.logging_setup import setup_logging
from portal.routes import router as api_router

logger = logging.getLogger(__name__)

WEB_DIST_DIR = ROOT_DIR / "web" / "dist"


def create_app() -> FastAPI:
    """Create and configure the FastAPI portal application."""
    app = FastAPI(title="SnapStudy Portal", docs_url=None, redoc_url=None)

    # Global unhandled exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.detail}
            )
        logger.error(
            "Unhandled error processing %s: %s", request.url.path, exc, exc_info=True
        )
        return JSONResponse(
            status_code=500, content={"detail": "internal_error"}
        )

    # Include API routes
    app.include_router(api_router)

    # Serve static frontend or fallback message
    if WEB_DIST_DIR.is_dir() and (WEB_DIST_DIR / "index.html").is_file():
        assets_dir = WEB_DIST_DIR / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            file_path = WEB_DIST_DIR / full_path
            if full_path and file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(WEB_DIST_DIR / "index.html")
    else:

        @app.get("/{full_path:path}")
        async def ui_not_built(full_path: str):
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
    """Run portal via uvicorn."""
    import uvicorn

    setup_logging(settings.LOG_LEVEL)
    init_db(settings.DATABASE_PATH)

    logger.info(
        "Starting SnapStudy Portal on http://%s:%d",
        settings.PORTAL_HOST,
        settings.PORTAL_PORT,
    )
    uvicorn.run(
        "portal.main:app",
        host=settings.PORTAL_HOST,
        port=settings.PORTAL_PORT,
        access_log=False,
    )


if __name__ == "__main__":
    main()

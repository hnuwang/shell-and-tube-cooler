from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as design_router


def create_app() -> FastAPI:
    """Create the FastAPI application instance."""
    app = FastAPI(
        title="Shell-and-Tube Cooler Design API",
        version="0.1.0",
        description="API wrapper for the course-design shell-and-tube cooler calculation engine.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(design_router, prefix="/api")
    return app


app = create_app()

import sys
import os
from pathlib import Path
from rich.console import Console
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .engine.storage import init_project_db


# Initialize the configuration and database
try:
    # Get config path from environment variable or use default
    config_path = os.environ.get('MULTINEAR_CONFIG')
    config_path = Path(config_path) if config_path else None

    # Initialize the database first
    init_project_db(config_path)

    # Create the FastAPI application with custom documentation URLs
    app = FastAPI(
        title="Multinear API",
        docs_url="/api/docs",            # Swagger UI
        redoc_url="/api/redoc",          # Redoc
        openapi_url="/api/openapi.json"  # OpenAPI JSON schema
    )

    # Add CORS middleware to handle cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],    # Allow all origins (update in production)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the API router with all endpoints
    app.include_router(api_router)

    # Serve the frontend static files (Svelte app)
    frontend_path = Path(__file__).parent.parent / "multinear" / "frontend" / "build"
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

except Exception as e:
    console = Console()
    console.print("[red bold]Error initializing Multinear:[/red bold]")

    console.print("[red]An unexpected error occurred:[/red]")
    console.print(f"[red]{str(e)}[/red]")
    if "--debug" in sys.argv:
        console.print_exception()

    sys.exit(1)

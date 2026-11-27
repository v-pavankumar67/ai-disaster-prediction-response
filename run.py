"""One-Click Launcher for AI Disaster Prediction & Response Platform."""

import sys
import time
import webbrowser
import threading
import uvicorn
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.database import engine, Base


def init_db():
    """Ensure database tables exist."""
    print("-> Initializing Database Models...")
    Base.metadata.create_all(bind=engine)
    print("-> Database verified successfully.")


def open_browser():
    """Opens browser after server has started."""
    time.sleep(1.5)
    url = f"http://{settings.HOST}:{settings.PORT}"
    print(f"-> Opening interactive GIS Command Center in browser: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    print("=" * 75)
    print("  AI DISASTER PREDICTION & RESPONSE PLATFORM")
    print("  Multi-Hazard AI • Spatial Physics Sim • Decision Triage • VRPTW Routing")
    print("=" * 75)
    print(f"  * Environment:    {settings.ENVIRONMENT}")
    print(f"  * Host / Port:    {settings.HOST}:{settings.PORT}")
    print(f"  * Dashboard UI:   http://{settings.HOST}:{settings.PORT}/")
    print(f"  * API Docs:       http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 75)

    init_db()

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start FastAPI Backend via Uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )


if __name__ == "__main__":
    main()

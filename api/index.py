# api/index.py
# Vercel serverless entrypoint — satisfies FastAPI framework detector
# and serves the static frontend with offline/mock API fallbacks.
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SPHEREx Hunter API", version="2.0.0")

@app.get("/api/health")
def health():
    return {"status": "ok", "note": "Full backend runs locally via uvicorn backend.main:app"}

# Mount frontend asset directories if present
if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
if (FRONTEND_DIR / "vendor").exists():
    app.mount("/vendor", StaticFiles(directory=str(FRONTEND_DIR / "vendor")), name="vendor")
if (FRONTEND_DIR / "src").exists():
    app.mount("/src", StaticFiles(directory=str(FRONTEND_DIR / "src")), name="src")
if (FRONTEND_DIR / "audio").exists():
    app.mount("/audio", StaticFiles(directory=str(FRONTEND_DIR / "audio")), name="audio")

@app.get("/favicon.svg")
def favicon():
    fav = FRONTEND_DIR / "favicon.svg"
    if fav.exists():
        return FileResponse(fav, media_type="image/svg+xml")
    return HTMLResponse("", status_code=204)

@app.get("/")
@app.get("/index.html")
@app.get("/app")
def serve_root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>SPHEREx Hunter: frontend/index.html not found</h1>", status_code=404)

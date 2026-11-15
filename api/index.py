# api/index.py
# Vercel serverless entrypoint stub — satisfies FastAPI framework detector.
# SPHEREx Hunter frontend is served statically from /frontend via vercel.json outputDirectory.
# Backend API routes are handled client-side with mock fallbacks when running standalone.
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI

app = FastAPI(title="SPHEREx Hunter API Stub", version="2.0.0")

@app.get("/api/health")
def health():
    return {"status": "ok", "note": "Full backend runs locally via uvicorn backend.main:app"}

# api/index.py
from fastapi import FastAPI

app = FastAPI(title="SPHEREx Hunter API", version="2.0.0")

@app.get("/api/health")
@app.get("/health")
def health():
    return {"status": "ok", "note": "Full backend runs locally via uvicorn backend.main:app"}

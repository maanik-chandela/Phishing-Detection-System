from contextlib import asynccontextmanager
from urllib.parse import urlsplit
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.ml.predictor import PhishingPredictor
from backend.risk.risk_engine import assess_risk
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
predictor = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    predictor = PhishingPredictor()
    yield
app = FastAPI(
    title="Phishing Detection API",
    description="Machine Learning-Based Phishing Risk Assessment",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
class URLRequest(BaseModel):
    url: str = Field(
        min_length=8,
        max_length=4096,
    )
@app.get("/health")
def health():
    return {
        "status": "running",
        "model_loaded": predictor is not None,
    }
@app.post("/analyze")
def analyze(request: URLRequest):
    url = request.url.strip()
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() not in ("http", "https"):
            raise ValueError(
                "Only HTTP and HTTPS URLs are supported."
            )
        if not parsed.hostname:
            raise ValueError("Invalid hostname.")
        result = predictor.predict(url)
        report = assess_risk(result)
        return report
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
# ============================================
# PHISHGUARD FRONTEND
# ============================================

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"
app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css"
)

app.mount(
    "/js",
    StaticFiles(directory=FRONTEND_DIR / "js"),
    name="js"
)
@app.get("/")
def serve_frontend():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )
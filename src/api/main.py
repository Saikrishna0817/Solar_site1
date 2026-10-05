"""SolarSite-India FastAPI server — prediction and data serving endpoints."""
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

app = FastAPI(
    title="SolarSite-India API",
    description="ML-powered solar site selection for India. Predicts CUF and suitability from 42 environmental, terrain, and infrastructure features.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    latitude: float = Field(..., ge=6.0, le=38.0, description="Latitude (6°N to 38°N for India)")
    longitude: float = Field(..., ge=68.0, le=98.0, description="Longitude (68°E to 98°E for India)")


class PredictionResponse(BaseModel):
    district: str
    state: str
    cuf_predicted: float
    suitability_score: float
    suitability_label: str
    ghi: float
    temperature: float
    model_version: str = "1.0.0"


class SiteSummary(BaseModel):
    district: str
    state: str
    cuf_predicted: float
    suitability_score: float
    ghi: float
    temperature: float
    elevation: float


class SiteDetail(BaseModel):
    district: str
    state: str
    latitude: float
    longitude: float
    cuf_predicted: float
    suitability_score: float
    suitability_label: str
    ghi: float
    dni: float
    temperature: float
    elevation: float
    slope: float
    land_use: str
    grid_distance: float


class HealthResponse(BaseModel):
    status: str
    model_version: str
    model_loaded: bool
    districts_available: int


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    from src.ml.config import Config
    cfg = Config()
    model_path = cfg.models_dir / "ridge.joblib"
    try:
        from src.api.services.data import load_processed_sites
        n_districts = len(load_processed_sites())  # cached; counts what /sites actually serves
    except Exception:
        n_districts = 0  # ponytail: corrupt CSV degrades to 0, not 500; fix the CSV, not this.
    return {
        "status": "healthy",
        "model_version": "1.0.0",
        "model_loaded": model_path.exists(),
        "districts_available": n_districts,
    }


@app.get("/api/v1/sites", response_model=list[SiteSummary])
async def list_sites(
    state: str = Query(None, description="Filter by state name"),
    min_suitability: float = Query(0.0, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    try:
        from src.api.services.data import load_processed_sites
        sites = load_processed_sites()
        if state:
            sites = [s for s in sites if s.get("state", "").lower() == state.lower()]
        sites = [s for s in sites if s.get("suitability_score", 1.0) >= min_suitability]
        return sites[offset : offset + limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sites/{district_id}", response_model=SiteDetail)
async def get_site(district_id: str):
    try:
        from src.api.services.data import load_site_detail
        site = load_site_detail(district_id)
        if site is None:
            raise HTTPException(status_code=404, detail=f"Site '{district_id}' not found")
        return site
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        from src.api.services.inference import predict_cuf
        result = predict_cuf(request.latitude, request.longitude)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/states")
async def list_states():
    try:
        from src.api.services.data import load_state_summary
        return load_state_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
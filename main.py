import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import create_document
from schemas import Booking

app = FastAPI(title="Clean Efficiency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Service(BaseModel):
    id: str
    title: str
    subtitle: str
    bullets: List[str]

class CaseStudy(BaseModel):
    id: str
    client: str
    title: str
    kpis: List[str]
    summary: str

SERVICES: List[Service] = [
    Service(
        id="advisory",
        title="AI Strategy & Advisory",
        subtitle="Roadmaps grounded in business value and operational reality",
        bullets=[
            "AI opportunity mapping",
            "Data readiness & governance",
            "Risk & compliance by design",
        ],
    ),
    Service(
        id="automation",
        title="Automation & Agents",
        subtitle="Deploy production-grade AI agents that actually ship work",
        bullets=[
            "Process automation",
            "Agentic workflows",
            "Enterprise integrations",
        ],
    ),
    Service(
        id="platform",
        title="AI Platform Engineering",
        subtitle="Foundation models, orchestration, observability, and scale",
        bullets=[
            "Model selection & evaluation",
            "Guardrails & safety",
            "MLOps & monitoring",
        ],
    ),
]

CASES: List[CaseStudy] = [
    CaseStudy(
        id="ops-efficiency",
        client="Global SaaS",
        title="Scaled support automation without sacrificing CSAT",
        kpis=[
            "+38% self-serve resolution",
            "-42% average handle time",
            "+11pts CSAT uplift",
        ],
        summary="Multi-agent triage, knowledge-grounded responses, and closed-loop learning across channels.",
    ),
    CaseStudy(
        id="rev-ops",
        client="Fintech",
        title="Revenue ops copilot for zero-lag pipeline intelligence",
        kpis=[
            "+19% win-rate",
            "-27% cycle time",
            "+24% rep productivity",
        ],
        summary="Unified data layer with retrieval-augmented insights and proactive risk surfacing via Slack.",
    ),
]

@app.get("/")
def read_root():
    return {"message": "Clean Efficiency API running"}

@app.get("/api/services", response_model=List[Service])
def get_services():
    return SERVICES

@app.get("/api/cases", response_model=List[CaseStudy])
def get_cases():
    return CASES

@app.post("/api/booking")
def create_booking(booking: Booking):
    try:
        booking_id = create_document("booking", booking)
        return {"ok": True, "id": booking_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(title="Worksite Secure API", version="0.1.0")

# =========================
# CORS – autoriser le Dashboard
# =========================
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://worksite-secure-dashboard.vercel.app",  # Front en prod (Vercel)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELES
# =========================

class Site(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    manager: Optional[str] = None
    risk_score: int = 0


class Incident(BaseModel):
    id: str
    site_id: str
    type: str
    severity: str
    description: str
    status: str
    created_at: datetime


class IncidentCreate(BaseModel):
    site_id: str
    type: str
    severity: str
    description: str


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None


# =========================
# "BASE DE DONNÉES" EN MÉMOIRE
# =========================

sites_db: List[Site] = [
    Site(
        id="1",
        name="Immeuble Plateau A",
        location="Localisation non précisée",
        manager="Non renseigné",
        risk_score=62,
    ),
    Site(
        id="2",
        name="Chantier Zone Industrielle",
        location="Localisation non précisée",
        manager="Non renseigné",
        risk_score=45,
    ),
    Site(
        id="3",
        name="Résidence Riviera Golf",
        location="Localisation non précisée",
        manager="Non renseigné",
        risk_score=80,
    ),
]

incidents_db: List[Incident] = [
    Incident(
        id="I1",
        site_id="1",
        type="Vol",
        severity="Moyen",
        description="Vol de ciment",
        status="Nouveau",
        created_at=datetime(2025, 12, 30, 8, 20, 13),
    ),
    Incident(
        id="I2",
        site_id="1",
        type="Accident",
        severity="Critique",
        description="Chute ouvrier",
        status="En cours",
        created_at=datetime(2025, 12, 30, 8, 20, 13),
    ),
    Incident(
        id="I3",
        site_id="2",
        type="Intrusion",
        severity="Mineur",
        description="Personne non autorisée",
        status="Résolu",
        created_at=datetime(2025, 12, 30, 8, 20, 13),
    ),
]


# =========================
# ENDPOINTS
# =========================

@app.get("/status")
def get_status():
    return {
        "app": "Worksite Secure",
        "status": "OK",
        "version": "0.1.0",
        "sites": len(sites_db),
        "incidents": len(incidents_db),
    }


@app.get("/sites", response_model=List[Site])
def list_sites():
    return sites_db


@app.get("/incidents", response_model=List[Incident])
def list_incidents():
    return incidents_db


@app.get("/incidents/open", response_model=List[Incident])
def list_open_incidents():
    return [
        inc
        for inc in incidents_db
        if inc.status.lower() not in ["resolu", "résolu"]
    ]


@app.post("/incidents", response_model=Incident, status_code=201)
def create_incident(payload: IncidentCreate):
    # Vérifier que le chantier existe
    site = next((s for s in sites_db if s.id == payload.site_id), None)
    if site is None:
        raise HTTPException(status_code=400, detail="Chantier inconnu.")

    new_incident = Incident(
        id=str(uuid.uuid4())[:8].upper(),
        site_id=payload.site_id,
        type=payload.type,
        severity=payload.severity,
        description=payload.description,
        status="Nouveau",
        created_at=datetime.utcnow(),
    )
    incidents_db.append(new_incident)
    return new_incident


@app.patch("/incidents/{incident_id}", response_model=Incident)
def update_incident(incident_id: str, payload: IncidentUpdate):
    incident = next((i for i in incidents_db if i.id == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident introuvable.")

    data = incident.dict()

    if payload.status is not None:
        data["status"] = payload.status
    if payload.severity is not None:
        data["severity"] = payload.severity
    if payload.description is not None:
        data["description"] = payload.description

    updated = Incident(**data)

    # Remplacer dans la "base"
    index = incidents_db.index(incident)
    incidents_db[index] = updated
    return updated

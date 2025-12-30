from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Worksite Secure API",
    description="MVP - Plateforme de sécurité et supervision des chantiers",
    version="0.1.0",
)

# 🔓 CORS : autoriser le frontend (Next.js) à appeler l’API depuis le navigateur
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # plus tard, tu pourras mettre seulement ton domaine frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SiteBase(BaseModel):
    name: str
    city: str
    manager_name: str
    risk_score: int = 50
    incidents_open: int = 0
    presence_today: int = 0
    presence_expected: int = 0


class Site(SiteBase):
    id: int


class SiteCreate(SiteBase):
    pass


class IncidentBase(BaseModel):
    site_id: int
    type: str
    severity: str
    description: Optional[str] = None
    status: str = "Nouveau"


class Incident(IncidentBase):
    id: int
    created_at: datetime


_sites: List[Site] = []
_incidents: List[Incident] = []
_site_id_counter = 1
_incident_id_counter = 1


def seed_demo_data():
    global _site_id_counter, _incident_id_counter

    if _sites:
        return

    demo_sites = [
        Site(
            id=1,
            name="Immeuble Plateau A",
            city="Abidjan",
            manager_name="Koffi",
            risk_score=62,
            incidents_open=2,
            presence_today=18,
            presence_expected=22,
        ),
        Site(
            id=2,
            name="Chantier Zone Industrielle",
            city="Yopougon",
            manager_name="Doumbia",
            risk_score=45,
            incidents_open=1,
            presence_today=25,
            presence_expected=28,
        ),
        Site(
            id=3,
            name="Résidence Riviera Golf",
            city="Cocody",
            manager_name="Konan",
            risk_score=80,
            incidents_open=3,
            presence_today=12,
            presence_expected=20,
        ),
    ]
    _sites.extend(demo_sites)
    _site_id_counter += len(demo_sites)

    demo_incidents = [
        Incident(
            id=1,
            site_id=1,
            type="Vol",
            severity="Moyen",
            description="Vol de ciment",
            status="Nouveau",
            created_at=datetime.utcnow(),
        ),
        Incident(
            id=2,
            site_id=1,
            type="Accident",
            severity="Critique",
            description="Chute ouvrier",
            status="En cours",
            created_at=datetime.utcnow(),
        ),
        Incident(
            id=3,
            site_id=2,
            type="Intrusion",
            severity="Mineur",
            description="Personne non autorisée",
            status="Résolu",
            created_at=datetime.utcnow(),
        ),
    ]
    _incidents.extend(demo_incidents)
    _incident_id_counter += len(demo_incidents)


seed_demo_data()


@app.get("/")
def root():
    return {"app": "Worksite Secure", "status": "OK"}


@app.get("/status")
def status():
    return {
        "app": "Worksite Secure",
        "status": "OK",
        "version": "0.1.0",
        "sites": len(_sites),
        "incidents": len(_incidents),
    }


@app.get("/sites", response_model=List[Site])
def list_sites():
    return _sites


@app.post("/sites", response_model=Site)
def create_site(site: SiteCreate):
    global _site_id_counter
    new_site = Site(id=_site_id_counter, **site.dict())
    _sites.append(new_site)
    _site_id_counter += 1
    return new_site


@app.get("/incidents", response_model=List[Incident])
def list_incidents(site_id: Optional[int] = None):
    if site_id:
        return [i for i in _incidents if i.site_id == site_id]
    return _incidents


@app.post("/incidents", response_model=Incident)
def create_incident(incident: IncidentBase):
    global _incident_id_counter

    if not any(s.id == incident.site_id for s in _sites):
        raise HTTPException(status_code=400, detail="Chantier inexistant")

    new_incident = Incident(
        id=_incident_id_counter,
        created_at=datetime.utcnow(),
        **incident.dict(),
    )
    _incidents.append(new_incident)
    _incident_id_counter += 1
    return new_incident

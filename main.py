# main.py — Worksite Secure API (version complète + CORS)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# -------------------------------------------------
# Création de l'application FastAPI
# -------------------------------------------------
app = FastAPI(
    title="Worksite Secure API",
    version="0.1.0",
    description="API de démo pour le suivi de la sécurité des chantiers."
)

# -------------------------------------------------
# CORS : autoriser le dashboard Next.js à appeler l'API
# -------------------------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # à activer plus tard quand tu déploieras le dashboard :
    "https://worksite-secure-dashboard.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # en dev tu peux mettre ["*"] si tu veux tout ouvrir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Modèles de données
# -------------------------------------------------
class Site(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    manager: Optional[str] = None
    risk_score: int  # 0–100


class Incident(BaseModel):
    id: int
    site_id: int
    type: str          # Vol, Accident, Intrusion...
    severity: str      # Critique, Moyen, Mineur
    description: str
    status: str        # Nouveau, En cours, Résolu
    created_at: datetime


# -------------------------------------------------
# Faux "petit" stockage en mémoire (pour la démo)
# -------------------------------------------------
sites_db: List[Site] = [
    Site(
        id=1,
        name="Immeuble Plateau A",
        location="Localisation non précisée",
        manager="Non renseigné",
        risk_score=62,
    ),
    Site(
        id=2,
        name="Chantier Zone Industrielle",
        location="Localisation non précisée",
        manager="Non renseigné",
        risk_score=45,
    ),
    Site(
        id=3,
        name="Résidence Riviera Golf",
        location="Localisation non précisée",
        manager="Non renseigné",
        risk_score=80,
    ),
]

incidents_db: List[Incident] = [
    Incident(
        id=1,
        site_id=1,
        type="Vol",
        severity="Moyen",
        description="Vol de ciment",
        status="Nouveau",
        created_at=datetime(2025, 12, 30, 8, 20, 13),
    ),
    Incident(
        id=2,
        site_id=1,
        type="Accident",
        severity="Critique",
        description="Chute ouvrier",
        status="En cours",
        created_at=datetime(2025, 12, 30, 8, 20, 13),
    ),
    Incident(
        id=3,
        site_id=2,
        type="Intrusion",
        severity="Mineur",
        description="Personne non autorisée",
        status="Résolu",
        created_at=datetime(2025, 12, 30, 8, 20, 13),
    ),
]


# -------------------------------------------------
# Fonctions utilitaires
# -------------------------------------------------
def compute_stats():
    total_sites = len(sites_db)
    total_incidents = len(incidents_db)

    if total_incidents == 0:
        resolved_pct = 0
    else:
        resolved = sum(1 for i in incidents_db if i.status.lower() == "résolu")
        resolved_pct = round(resolved * 100 / total_incidents)

    critical_incidents = sum(
        1 for i in incidents_db if i.severity.lower() == "critique"
    )

    return {
        "total_sites": total_sites,
        "total_incidents": total_incidents,
        "resolved_percentage": resolved_pct,
        "critical_incidents": critical_incidents,
    }


# -------------------------------------------------
# Routes API
# -------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Worksite Secure API",
        "docs": "/docs",
        "status_endpoint": "/status",
    }


@app.get("/status")
def get_status():
    """
    Endpoint simple pour le check de santé de l'API.
    Utilisé par le dashboard pour savoir si le backend est en ligne.
    """
    stats = compute_stats()
    return {
        "app": "Worksite Secure",
        "status": "OK",
        "version": "0.1.0",
        "sites": stats["total_sites"],
        "incidents": stats["total_incidents"],
    }


@app.get("/sites", response_model=List[Site])
def list_sites():
    return sites_db


@app.get("/incidents", response_model=List[Incident])
def list_incidents():
    return incidents_db


@app.get("/stats")
def get_stats():
    """
    Statistiques globales pour alimenter les cartes du dashboard DG.
    """
    return compute_stats()


# -------------------------------------------------
# Lancement local (Render utilise déjà gunicorn/uvicorn via start command)
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)

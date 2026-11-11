
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from backend.calculs import simulation


# Chemins absolus
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Application
app = FastAPI(
    title="FruitFlow - Concentration de Fruits",
    version="1.0.0"
)

# Fichiers CSS et JavaScript
app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

# Templates HTML
templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# Page principale
@app.get("/", response_class=HTMLResponse)
async def accueil(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# Test du serveur
@app.get("/health")
async def health():
    return {
        "status": "OK",
        "application": "FruitFlow"
    }


# Données reçues depuis JavaScript
class Donnees(BaseModel):
    debit: float = Field(gt=20)
    ajout: float = Field(ge=0)
    concentration: float = Field(gt=0, le=100)
    temperature: float = Field(ge=20)


# Calcul de simulation
@app.post("/calcul")
async def calculer(d: Donnees):
    try:
        resultats = simulation(
            d.debit,
            d.ajout,
            d.concentration,
            d.temperature
        )

        return resultats

    except ValueError as erreur:
        raise HTTPException(
            status_code=400,
            detail=str(erreur)
        )

    except Exception as erreur:
        print("ERREUR DE CALCUL :", erreur)

        raise HTTPException(
            status_code=500,
            detail="Erreur interne pendant la simulation."
        )

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import Base, engine
from app.models.lead import Lead  # noqa: F401 (ensures model is registered)

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lead Intelligence API",
    description="Enrichment, deduplication, validation, and AI scoring for scraped B2B leads.",
    version="1.0.0",
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "lead-intelligence-api"}
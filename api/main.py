"""
DocQuery FastAPI Application
REST API for the RAG-powered documentation chatbot.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import chat, ingest, gaps as gaps_routes
from query.memory import init_memory_db
from gaps.tracker import init_gaps_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize databases on startup."""
    init_memory_db()
    init_gaps_db()
    yield


app = FastAPI(
    title="DocQuery API",
    description="RAG-powered documentation chatbot API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(gaps_routes.router, prefix="/api", tags=["Content Gaps"])


@app.get("/")
async def root():
    return {
        "name": "DocQuery API",
        "version": "1.0.0",
        "description": "RAG-powered documentation chatbot",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}

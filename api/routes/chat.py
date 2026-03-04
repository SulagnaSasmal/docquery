"""Chat API endpoint — the main RAG query interface."""

import uuid
from fastapi import APIRouter
from pydantic import BaseModel

from query.chain import RAGChain
from query.confidence import assess_confidence
from gaps.tracker import log_gap

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    session_id: str = ""
    collection: str = "default"


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    confidence: str
    confidence_score: float
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Ask a question about your documentation."""
    session_id = request.session_id or str(uuid.uuid4())

    chain = RAGChain(
        collection_name=request.collection,
        site_name=request.collection,
    )

    result = chain.query(
        question=request.question,
        session_id=session_id,
    )

    # Log content gap if low confidence
    if result.confidence == "low":
        nearest = ""
        if result.sources:
            nearest = result.sources[0].get("section", "")

        log_gap(
            question=request.question,
            collection=request.collection,
            session_id=session_id,
            confidence_score=result.confidence_score,
            top_retrieval_score=result.sources[0]["score"] if result.sources else 0,
            nearest_section=nearest,
        )

    return ChatResponse(
        answer=result.answer,
        sources=result.sources,
        confidence=result.confidence,
        confidence_score=result.confidence_score,
        session_id=session_id,
    )

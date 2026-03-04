"""
DocQuery Query — Confidence Scoring
Determines confidence level based on retrieval quality.
"""

from dataclasses import dataclass
from query.retriever import RetrievedChunk


@dataclass
class ConfidenceResult:
    """Confidence assessment for a query response."""
    level: str          # "high", "medium", "low"
    score: float        # 0.0 - 1.0
    top_chunk_score: float
    reason: str


def assess_confidence(
    chunks: list[RetrievedChunk],
    high_threshold: float = 0.85,
    medium_threshold: float = 0.70,
) -> ConfidenceResult:
    """
    Assess confidence based on retrieval scores.

    - HIGH: top chunk score > 0.85
    - MEDIUM: top chunk score 0.70 - 0.85
    - LOW: top chunk score < 0.70
    """
    if not chunks:
        return ConfidenceResult(
            level="low",
            score=0.0,
            top_chunk_score=0.0,
            reason="No relevant documents found.",
        )

    top_score = chunks[0].score

    # Average of top 3 scores for more robust assessment
    top_scores = [c.score for c in chunks[:3]]
    avg_score = sum(top_scores) / len(top_scores)

    if top_score >= high_threshold:
        return ConfidenceResult(
            level="high",
            score=avg_score,
            top_chunk_score=top_score,
            reason="Strong match found in documentation.",
        )
    elif top_score >= medium_threshold:
        return ConfidenceResult(
            level="medium",
            score=avg_score,
            top_chunk_score=top_score,
            reason="Partial match found. Answer may be incomplete.",
        )
    else:
        return ConfidenceResult(
            level="low",
            score=avg_score,
            top_chunk_score=top_score,
            reason="No strong match found. This topic may not be covered in the documentation.",
        )

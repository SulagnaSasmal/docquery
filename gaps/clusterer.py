"""
DocQuery Gaps — Question Clusterer

Groups similar low-confidence questions into topic clusters to surface
documentation themes. Uses difflib.SequenceMatcher (stdlib) — no extra deps.
"""

from difflib import SequenceMatcher
from dataclasses import dataclass, field


@dataclass
class GapCluster:
    """A cluster of semantically similar documentation gap questions."""

    representative: str   # The most-asked (canonical) question for this cluster
    questions: list[str]  # All questions merged into this cluster
    total_count: int      # Aggregate times asked across all variant questions
    min_confidence: float # Lowest confidence score seen in this cluster
    nearest_section: str  # Most common nearest_section value
    first_asked: str
    last_asked: str


def _similarity(a: str, b: str) -> float:
    """Normalised similarity ratio between two strings (case-insensitive)."""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _most_common_section(gaps: list[dict]) -> str:
    """Return the nearest_section that appears most often in a set of gaps."""
    counts: dict[str, int] = {}
    for g in gaps:
        s = g.get("nearest_section", "") or ""
        if s:
            counts[s] = counts.get(s, 0) + g.get("count", 1)
    return max(counts, key=counts.get) if counts else ""


def cluster_gaps(gaps: list[dict], threshold: float = 0.55) -> list["GapCluster"]:
    """
    Group gap questions into clusters by surface similarity.

    Args:
        gaps:      List of gap dicts from tracker.get_gaps().
                   Expected keys: question, count, min_confidence,
                   nearest_section, first_asked, last_asked.
        threshold: Similarity ratio above which two questions are merged.
                   0.55 handles typical paraphrasing of short questions.
                   Lower = more aggressive merging.

    Returns:
        List of GapCluster objects, sorted by total_count descending.

    Example:
        "How does OAuth work?"  ──┐
        "Explain OAuth flow"    ──┤─► cluster: "How does OAuth work?" (2x)
    """
    if not gaps:
        return []

    # Sort by count descending so the most-asked question becomes representative
    sorted_gaps = sorted(gaps, key=lambda g: g.get("count", 1), reverse=True)

    clusters: list[GapCluster] = []
    assigned: set[int] = set()

    for i, gap in enumerate(sorted_gaps):
        if i in assigned:
            continue

        # Seed this cluster with the current (highest-count) question
        members = [gap]
        assigned.add(i)

        for j, other in enumerate(sorted_gaps):
            if j in assigned:
                continue
            if _similarity(gap["question"], other["question"]) >= threshold:
                members.append(other)
                assigned.add(j)

        total_count = sum(m.get("count", 1) for m in members)
        min_conf = min(m.get("min_confidence", 0.0) for m in members)
        first = min((m.get("first_asked", "") for m in members), default="")
        last = max((m.get("last_asked", "") for m in members), default="")

        clusters.append(
            GapCluster(
                representative=gap["question"],
                questions=[m["question"] for m in members],
                total_count=total_count,
                min_confidence=min_conf,
                nearest_section=_most_common_section(members),
                first_asked=first,
                last_asked=last,
            )
        )

    return sorted(clusters, key=lambda c: c.total_count, reverse=True)

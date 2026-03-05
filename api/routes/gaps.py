"""Content gaps API — view, cluster, export, and manage documentation gaps."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

from gaps.tracker import get_gaps, update_gap_status
from gaps.clusterer import cluster_gaps
from gaps.reporter import generate_markdown_report, generate_csv_report

router = APIRouter()


@router.get("/gaps")
async def list_gaps(collection: str = "default", status: str = "open", limit: int = 50):
    """List raw content gaps for a collection (one row per distinct question)."""
    return get_gaps(collection, status=status, limit=limit)


@router.get("/gaps/clusters")
async def list_clustered_gaps(collection: str = "default", status: str = "open"):
    """
    List content gaps grouped into similarity clusters.

    Questions with similar wording are merged into one cluster so you can
    see that 'How does OAuth work?' and 'Explain OAuth flow' are the same gap.
    """
    gaps = get_gaps(collection, status=status)
    clusters = cluster_gaps(gaps)
    return [
        {
            "representative": c.representative,
            "questions": c.questions,
            "total_count": c.total_count,
            "min_confidence": round(c.min_confidence, 2),
            "nearest_section": c.nearest_section,
            "first_asked": c.first_asked,
            "last_asked": c.last_asked,
            "priority": (
                "high" if c.total_count >= 3
                else "medium" if c.total_count == 2
                else "low"
            ),
        }
        for c in clusters
    ]


@router.get("/gaps/report", response_class=PlainTextResponse)
async def gap_report_markdown(collection: str = "default"):
    """Generate a Markdown content-gap report with clustered questions."""
    return generate_markdown_report(collection)


@router.get("/gaps/export/csv")
async def gap_report_csv(collection: str = "default"):
    """Export content gaps as CSV (spreadsheet-ready, one row per cluster)."""
    csv_content = generate_csv_report(collection)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=gaps-{collection}.csv"
        },
    )


@router.patch("/gaps/{gap_id}")
async def update_gap(gap_id: int, status: str = "resolved"):
    """Update a gap's status: open | reviewing | resolved | out_of_scope."""
    update_gap_status(gap_id, status)
    return {"status": "updated", "gap_id": gap_id, "new_status": status}

"""Content gaps API endpoint — view and manage documentation gaps."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from gaps.tracker import get_gaps, update_gap_status, get_gap_report

router = APIRouter()


@router.get("/gaps")
async def list_gaps(collection: str = "default", status: str = "open", limit: int = 50):
    """Get content gaps for a collection."""
    return get_gaps(collection, status=status, limit=limit)


@router.patch("/gaps/{gap_id}")
async def update_gap(gap_id: int, status: str = "resolved"):
    """Update a gap's status (resolved, out_of_scope)."""
    update_gap_status(gap_id, status)
    return {"status": "updated", "gap_id": gap_id, "new_status": status}


@router.get("/gaps/report", response_class=PlainTextResponse)
async def gap_report(collection: str = "default"):
    """Generate a Markdown content gap report."""
    return get_gap_report(collection)

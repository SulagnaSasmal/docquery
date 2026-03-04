"""Ingestion API endpoint — trigger doc site crawling and embedding."""

import asyncio
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from ingestion.crawler import crawl_site
from ingestion.chunker import SectionAwareChunker
from ingestion.embedder import DocEmbedder, list_collections

router = APIRouter()


class IngestRequest(BaseModel):
    url: str
    collection_name: str = "default"
    max_pages: int = 100


class IngestResponse(BaseModel):
    status: str
    pages_crawled: int
    chunks_created: int
    collection: str


@router.post("/ingest", response_model=IngestResponse)
async def ingest_docs(request: IngestRequest):
    """Crawl a documentation site and store embeddings."""
    # Crawl
    pages = await crawl_site(
        url=request.url,
        max_pages=request.max_pages,
    )

    # Chunk
    chunker = SectionAwareChunker()
    all_chunks = []
    for page in pages:
        chunks = chunker.chunk_page(
            content=page.content,
            source_url=page.url,
            title=page.title,
            doc_type=page.doc_type,
        )
        all_chunks.extend(chunks)

    # Embed and store
    embedder = DocEmbedder(collection_name=request.collection_name)
    stored = embedder.embed_and_store(all_chunks)

    return IngestResponse(
        status="success",
        pages_crawled=len(pages),
        chunks_created=stored,
        collection=request.collection_name,
    )


@router.get("/collections")
async def get_collections():
    """List all indexed documentation collections."""
    collections = list_collections()
    return collections

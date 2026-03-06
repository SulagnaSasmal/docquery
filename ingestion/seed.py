"""
DocQuery — Demo Seed
Crawls and indexes the VaultPay demo documentation on cold start.
Runs automatically when AUTO_SEED=true (set in render.yaml).
Skips if the collection already has data (prevents double-indexing).
"""

import os
import asyncio

import chromadb

from ingestion.crawler import crawl_site
from ingestion.chunker import SectionAwareChunker
from ingestion.embedder import DocEmbedder

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data")

# Demo collections to seed on startup.
# Each entry: (collection_name, site_url, label_for_logs)
DEMO_COLLECTIONS = [
    (
        "vaultpay",
        "https://sulagnasasmal.github.io/vaultpay-api-docs/",
        "VaultPay API Docs",
    ),
]


def collection_is_empty(collection_name: str) -> bool:
    """Return True if the collection doesn't exist or has zero chunks."""
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        col = client.get_collection(collection_name)
        return col.count() == 0
    except Exception:
        return True


async def seed_collection(collection_name: str, url: str, label: str) -> int:
    """Crawl a doc site and embed it into ChromaDB. Returns chunk count."""
    print(f"[seed] Crawling {label} …")
    pages = await crawl_site(url=url, max_pages=50)
    print(f"[seed] Crawled {len(pages)} pages from {label}")

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

    if not all_chunks:
        print(f"[seed] No chunks extracted from {label} — skipping")
        return 0

    print(f"[seed] Embedding {len(all_chunks)} chunks for {label} …")
    embedder = DocEmbedder(collection_name=collection_name)
    stored = embedder.embed_and_store(all_chunks)
    print(f"[seed] Stored {stored} chunks into '{collection_name}' collection")
    return stored


async def run_demo_seed():
    """Seed all demo collections that are currently empty.
    Called from api/main.py lifespan on startup."""
    if os.getenv("AUTO_SEED", "").lower() != "true":
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("[seed] Skipping demo seed — OPENAI_API_KEY not set")
        return

    for collection_name, url, label in DEMO_COLLECTIONS:
        if collection_is_empty(collection_name):
            try:
                await seed_collection(collection_name, url, label)
            except Exception as exc:
                # Never crash the server over a failed seed
                print(f"[seed] WARNING: Failed to seed {label}: {exc}")
        else:
            count = chromadb.PersistentClient(path=CHROMA_DB_PATH).get_collection(collection_name).count()
            print(f"[seed] '{collection_name}' already has {count} chunks — skipping")

"""
DocQuery — Demo Seed
Crawls and indexes demo documentation collections on cold start.
Runs automatically when AUTO_SEED=true (set in render.yaml).
Skips collections that already have data (prevents double-indexing).
"""

import os
import asyncio

import chromadb

from ingestion.crawler import crawl_site
from ingestion.chunker import SectionAwareChunker
from ingestion.embedder import DocEmbedder

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data")

_SUNBRIDGE_BASE = "https://sulagnasasmal.github.io/enterprise-investment-management-platform-docs/"

# Demo collections to seed on startup.
# Each entry: dict with collection_name, url, label, and optional extra_urls.
# extra_urls is needed when a site uses JS-rendered navigation (links invisible
# to a static HTML crawler) — list every page URL explicitly.
DEMO_COLLECTIONS = [
    {
        "collection": "vaultpay",
        "url": "https://sulagnasasmal.github.io/vaultpay-api-docs/",
        "label": "VaultPay API Docs",
        "extra_urls": [],
    },
    {
        "collection": "sunbridge",
        "url": _SUNBRIDGE_BASE,
        "label": "SunBridge Asset Atrium Manager Docs",
        "extra_urls": [
            _SUNBRIDGE_BASE + "platform-overview.html",
            _SUNBRIDGE_BASE + "system-architecture.html",
            _SUNBRIDGE_BASE + "high-availability-enhancement.html",
            _SUNBRIDGE_BASE + "batch-processing-framework.html",
            _SUNBRIDGE_BASE + "multi-time-zone-processing.html",
            _SUNBRIDGE_BASE + "failover-and-audit-design.html",
            _SUNBRIDGE_BASE + "database-and-configuration-updates.html",
            _SUNBRIDGE_BASE + "release-impact-summary.html",
        ],
    },
]


def collection_is_empty(collection_name: str) -> bool:
    """Return True if the collection doesn't exist or has zero chunks."""
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        col = client.get_collection(collection_name)
        return col.count() == 0
    except Exception:
        return True


async def seed_collection(
    collection_name: str,
    url: str,
    label: str,
    extra_urls: list[str] | None = None,
) -> int:
    """Crawl a doc site and embed it into ChromaDB. Returns chunk count."""
    print(f"[seed] Crawling {label} …")
    pages = await crawl_site(url=url, extra_urls=extra_urls, max_pages=100)
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

    for entry in DEMO_COLLECTIONS:
        name = entry["collection"]
        if collection_is_empty(name):
            try:
                await seed_collection(
                    collection_name=name,
                    url=entry["url"],
                    label=entry["label"],
                    extra_urls=entry.get("extra_urls"),
                )
            except Exception as exc:
                # Never crash the server over a failed seed
                print(f"[seed] WARNING: Failed to seed {entry['label']}: {exc}")
        else:
            count = (
                chromadb.PersistentClient(path=CHROMA_DB_PATH)
                .get_collection(name)
                .count()
            )
            print(f"[seed] '{name}' already has {count} chunks — skipping")

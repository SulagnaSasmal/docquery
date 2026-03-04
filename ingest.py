#!/usr/bin/env python3
"""
DocQuery CLI — Ingest documentation sites into the vector database.

Usage:
    python ingest.py --url https://your-docs-site.com --collection my-docs
    python ingest.py --url https://your-docs-site.com --collection my-docs --refresh
"""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from ingestion.crawler import crawl_site
from ingestion.chunker import SectionAwareChunker
from ingestion.embedder import DocEmbedder


async def main():
    parser = argparse.ArgumentParser(description="DocQuery — Ingest documentation for RAG")
    parser.add_argument("--url", required=True, help="Base URL of the documentation site to crawl")
    parser.add_argument("--collection", default="default", help="Collection name in ChromaDB")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum pages to crawl")
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum crawl depth")
    parser.add_argument("--refresh", action="store_true", help="Re-ingest (deletes existing collection)")

    args = parser.parse_args()

    print(f"\nDocQuery Ingestion Pipeline")
    print(f"{'=' * 40}")
    print(f"URL: {args.url}")
    print(f"Collection: {args.collection}")
    print(f"Max pages: {args.max_pages}")
    print()

    # Refresh: delete existing collection
    if args.refresh:
        try:
            embedder = DocEmbedder(collection_name=args.collection)
            embedder.delete_collection()
            print(f"Deleted existing collection: {args.collection}\n")
        except Exception:
            pass

    # Step 1: Crawl
    print("Step 1: Crawling documentation site...")
    pages = await crawl_site(
        url=args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
    )
    print(f"Crawled {len(pages)} pages.\n")

    if not pages:
        print("No pages found. Check the URL and try again.")
        sys.exit(1)

    # Step 2: Chunk
    print("Step 2: Splitting into section-aware chunks...")
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
    print(f"Created {len(all_chunks)} chunks.\n")

    # Step 3: Embed and store
    print("Step 3: Embedding and storing in ChromaDB...")
    embedder = DocEmbedder(collection_name=args.collection)
    stored = embedder.embed_and_store(all_chunks)

    print(f"\nDone!")
    print(f"{'=' * 40}")
    print(f"Pages crawled: {len(pages)}")
    print(f"Chunks created: {stored}")
    print(f"Collection: {args.collection}")
    print(f"\nYou can now query your docs:")
    print(f"  python query_cli.py --collection {args.collection}")
    print(f"  or start the API: uvicorn api.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())

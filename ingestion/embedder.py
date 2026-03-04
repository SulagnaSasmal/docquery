"""
DocQuery Ingestion — Embedding & ChromaDB Storage
Embeds document chunks and stores them in ChromaDB.
"""

import os
from datetime import datetime

import chromadb
from chromadb.config import Settings
from openai import OpenAI

from ingestion.chunker import DocChunk

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


class DocEmbedder:
    """Embeds document chunks and stores them in ChromaDB."""

    def __init__(self, collection_name: str = "default"):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.openai = OpenAI()
        self.collection_name = collection_name

    def embed_and_store(self, chunks: list[DocChunk]) -> int:
        """Embed chunks and store in ChromaDB. Returns count of stored chunks."""
        if not chunks:
            return 0

        batch_size = 100
        total_stored = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            texts = [chunk.text for chunk in batch]
            metadatas = []
            ids = []

            for j, chunk in enumerate(batch):
                chunk_id = f"{self.collection_name}_{i + j}_{hash(chunk.text) % 100000}"
                ids.append(chunk_id)

                meta = {
                    "source_url": chunk.metadata.get("source_url", ""),
                    "title": chunk.metadata.get("title", ""),
                    "section_path": chunk.metadata.get("section_path", ""),
                    "doc_type": chunk.metadata.get("doc_type", ""),
                    "heading_level": chunk.metadata.get("heading_level", 0),
                    "has_code": chunk.metadata.get("has_code", False),
                    "has_table": chunk.metadata.get("has_table", False),
                    "token_count": chunk.token_count,
                    "indexed_at": datetime.utcnow().isoformat(),
                }
                metadatas.append(meta)

            # Generate embeddings
            embeddings = self._embed_texts(texts)

            # Store in ChromaDB
            self.collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            total_stored += len(batch)
            print(f"  Stored {total_stored}/{len(chunks)} chunks")

        return total_stored

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using OpenAI API."""
        response = self.openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def get_collection_info(self) -> dict:
        """Get info about the current collection."""
        count = self.collection.count()
        return {
            "name": self.collection_name,
            "chunks": count,
            "path": CHROMA_DB_PATH,
        }

    def delete_collection(self):
        """Delete the current collection."""
        self.client.delete_collection(self.collection_name)
        print(f"Deleted collection: {self.collection_name}")


def list_collections() -> list[dict]:
    """List all collections in the ChromaDB."""
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collections = client.list_collections()
    results = []
    for col in collections:
        results.append({
            "name": col.name,
            "chunks": col.count(),
        })
    return results

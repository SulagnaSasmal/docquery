"""
DocQuery Query — Vector Retriever
Retrieves relevant document chunks from ChromaDB.
"""

import os
from dataclasses import dataclass, field

import chromadb
from openai import OpenAI

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


@dataclass
class RetrievedChunk:
    """A retrieved document chunk with relevance score."""
    text: str
    score: float
    metadata: dict = field(default_factory=dict)


class DocRetriever:
    """Retrieves relevant chunks from ChromaDB using vector similarity."""

    def __init__(self, collection_name: str = "default"):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_collection(name=collection_name)
        self.openai = OpenAI()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        doc_type: str | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve top-k most relevant chunks for a query."""
        # Generate query embedding
        response = self.openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[query],
        )
        query_embedding = response.data[0].embedding

        # Build where filter
        where_filter = None
        if doc_type:
            where_filter = {"doc_type": doc_type}

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                # ChromaDB returns distances; convert to similarity score
                distance = results["distances"][0][i] if results["distances"] else 0
                # Cosine distance to similarity: 1 - distance
                score = max(0, 1 - distance)

                metadata = results["metadatas"][0][i] if results["metadatas"] else {}

                chunks.append(RetrievedChunk(
                    text=doc,
                    score=round(score, 4),
                    metadata=metadata,
                ))

        # Sort by score descending
        chunks.sort(key=lambda c: c.score, reverse=True)
        return chunks

    def retrieve_with_context(
        self,
        query: str,
        conversation_history: list[dict] | None = None,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve with optional conversation context for follow-up questions."""
        if conversation_history:
            # Reformulate query using conversation context
            context_query = self._reformulate_query(query, conversation_history)
        else:
            context_query = query

        return self.retrieve(context_query, top_k=top_k)

    def _reformulate_query(
        self, query: str, history: list[dict]
    ) -> str:
        """Use LLM to reformulate follow-up questions for better retrieval."""
        recent_history = history[-4:]  # Last 2 exchanges
        history_text = ""
        for msg in recent_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Reformulate the user's follow-up question into a standalone search query. "
                    "Use the conversation history for context. Output ONLY the reformulated query, nothing else.",
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n{history_text}\nFollow-up question: {query}\n\nReformulated query:",
                },
            ],
            temperature=0,
            max_tokens=100,
        )

        reformulated = response.choices[0].message.content.strip()
        return reformulated or query

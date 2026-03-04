"""
DocQuery Query — RAG Chain
The main RAG pipeline: retrieval + generation with citations.
"""

import os
from dataclasses import dataclass, field

from openai import OpenAI

from query.retriever import DocRetriever, RetrievedChunk
from query.confidence import assess_confidence, ConfidenceResult
from query.memory import get_history, add_message

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """You are DocQuery, a documentation assistant for {site_name}.

Rules:
1. Answer ONLY using the provided context from the documentation. Never use prior knowledge.
2. If the context doesn't contain enough information, say: "I couldn't find a clear answer in the documentation for this."
3. Always cite your sources using [Source: page_title](url) format.
4. If multiple sections are relevant, synthesize them into a coherent answer.
5. For code examples, reproduce them exactly as they appear in the docs.
6. Be concise. Match the tone of the documentation.
7. If the user's question is ambiguous, ask for clarification.

Context from documentation:
{context}
"""


@dataclass
class QueryResponse:
    """Response from the RAG chain."""
    answer: str
    sources: list[dict] = field(default_factory=list)
    confidence: str = "medium"
    confidence_score: float = 0.0
    session_id: str = ""


class RAGChain:
    """Main RAG pipeline for answering questions from documentation."""

    def __init__(self, collection_name: str = "default", site_name: str = ""):
        self.retriever = DocRetriever(collection_name=collection_name)
        self.openai = OpenAI()
        self.site_name = site_name or collection_name
        self.collection_name = collection_name

    def query(
        self,
        question: str,
        session_id: str = "default",
        top_k: int = 5,
    ) -> QueryResponse:
        """Run the full RAG pipeline: retrieve → contextualize → generate."""
        # Get conversation history for context
        history = get_history(session_id, limit=10)

        # Retrieve relevant chunks
        chunks = self.retriever.retrieve_with_context(
            query=question,
            conversation_history=history if history else None,
            top_k=top_k,
        )

        # Assess confidence
        confidence_result = assess_confidence(chunks)

        # Build context from retrieved chunks
        context = self._build_context(chunks)

        # Build messages
        system_message = SYSTEM_PROMPT.format(
            site_name=self.site_name,
            context=context,
        )

        messages = [{"role": "system", "content": system_message}]

        # Add conversation history (last 6 messages)
        for msg in history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        messages.append({"role": "user", "content": question})

        # Add confidence hint if low
        if confidence_result.level == "low":
            messages.append({
                "role": "system",
                "content": "Note: The retrieved context has low relevance to this question. "
                "Indicate in your response that you're not fully confident and the documentation may not cover this topic.",
            })

        # Generate response
        response = self.openai.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=1000,
        )

        answer = response.choices[0].message.content.strip()

        # Build source citations
        sources = self._build_sources(chunks)

        # Save to conversation memory
        add_message(session_id, "user", question)
        add_message(
            session_id,
            "assistant",
            answer,
            sources=sources,
            confidence=confidence_result.level,
        )

        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=confidence_result.level,
            confidence_score=confidence_result.score,
            session_id=session_id,
        )

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source_url = chunk.metadata.get("source_url", "")
            title = chunk.metadata.get("title", "")
            section = chunk.metadata.get("section_path", "")

            header = f"[Document {i}: {title}"
            if section:
                header += f" > {section}"
            header += f"]({source_url})"

            context_parts.append(f"{header}\n{chunk.text}")

        return "\n\n---\n\n".join(context_parts)

    def _build_sources(self, chunks: list[RetrievedChunk]) -> list[dict]:
        """Build source citation list from retrieved chunks."""
        sources = []
        seen_urls = set()

        for chunk in chunks:
            url = chunk.metadata.get("source_url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            section = chunk.metadata.get("section_path", "")
            anchor = ""
            if section:
                anchor = "#" + section.split(" > ")[-1].lower().replace(" ", "-")

            sources.append({
                "title": chunk.metadata.get("title", "Unknown"),
                "url": url + anchor,
                "section": section,
                "score": chunk.score,
                "doc_type": chunk.metadata.get("doc_type", ""),
            })

        return sources[:5]  # Limit to top 5 unique sources

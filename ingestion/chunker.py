"""
DocQuery Ingestion — Section-Aware Chunker
Splits documentation into semantically meaningful chunks
that preserve heading hierarchy and code blocks.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

import tiktoken


@dataclass
class DocChunk:
    """A single documentation chunk with rich metadata."""
    text: str
    metadata: dict = field(default_factory=dict)
    token_count: int = 0


class SectionAwareChunker:
    """
    Documentation-optimized text splitter.

    Unlike naive fixed-size chunking, this splitter:
    - Splits on heading boundaries (H1, H2, H3)
    - Never splits inside code blocks or tables
    - Preserves section hierarchy as metadata
    - Adds token overlap between chunks
    """

    def __init__(
        self,
        max_tokens: int = 800,
        overlap_tokens: int = 100,
        model: str = "cl100k_base",
    ):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.tokenizer = tiktoken.get_encoding(model)

    def chunk_page(
        self,
        content: str,
        source_url: str = "",
        title: str = "",
        doc_type: str = "conceptual",
    ) -> list[DocChunk]:
        """Split a documentation page into section-aware chunks."""
        sections = self._split_by_headings(content)
        chunks = []

        section_path_stack = []

        for section in sections:
            heading = section.get("heading", "")
            level = section.get("level", 0)
            body = section.get("body", "").strip()

            if not body and not heading:
                continue

            # Update section path based on heading level
            if heading and level > 0:
                # Pop to the correct level
                while len(section_path_stack) >= level:
                    section_path_stack.pop()
                section_path_stack.append(heading)

            section_path = " > ".join(section_path_stack)

            # Combine heading with body
            full_text = f"{heading}\n{body}" if heading else body
            tokens = self._count_tokens(full_text)

            has_code = "```" in body or "<code>" in body
            has_table = "|" in body and body.count("|") > 3

            base_metadata = {
                "source_url": source_url,
                "title": title,
                "section_path": section_path,
                "doc_type": doc_type,
                "heading_level": level,
                "has_code": has_code,
                "has_table": has_table,
            }

            if tokens <= self.max_tokens:
                chunk = DocChunk(
                    text=full_text,
                    metadata=base_metadata.copy(),
                    token_count=tokens,
                )
                chunks.append(chunk)
            else:
                # Section too large — split by paragraphs within section
                sub_chunks = self._split_large_section(
                    full_text, base_metadata
                )
                chunks.extend(sub_chunks)

        # Add overlap between chunks
        chunks = self._add_overlap(chunks)

        return chunks

    def _split_by_headings(self, content: str) -> list[dict]:
        """Split content by markdown heading boundaries."""
        sections = []
        current_heading = ""
        current_level = 0
        current_body_lines = []

        for line in content.split("\n"):
            heading_match = re.match(r"^(#{1,4})\s+(.+)$", line)

            if heading_match:
                # Save previous section
                if current_body_lines or current_heading:
                    sections.append({
                        "heading": current_heading,
                        "level": current_level,
                        "body": "\n".join(current_body_lines),
                    })
                    current_body_lines = []

                current_level = len(heading_match.group(1))
                current_heading = heading_match.group(2).strip()
            else:
                current_body_lines.append(line)

        # Don't forget the last section
        if current_body_lines or current_heading:
            sections.append({
                "heading": current_heading,
                "level": current_level,
                "body": "\n".join(current_body_lines),
            })

        return sections

    def _split_large_section(
        self, text: str, base_metadata: dict
    ) -> list[DocChunk]:
        """Split a large section by paragraph boundaries, keeping code blocks intact."""
        chunks = []
        blocks = self._extract_blocks(text)

        current_text = ""
        current_tokens = 0

        for block in blocks:
            block_tokens = self._count_tokens(block)

            if current_tokens + block_tokens > self.max_tokens and current_text:
                chunks.append(DocChunk(
                    text=current_text.strip(),
                    metadata=base_metadata.copy(),
                    token_count=current_tokens,
                ))
                current_text = ""
                current_tokens = 0

            current_text += block + "\n"
            current_tokens += block_tokens

        if current_text.strip():
            chunks.append(DocChunk(
                text=current_text.strip(),
                metadata=base_metadata.copy(),
                token_count=current_tokens,
            ))

        return chunks

    def _extract_blocks(self, text: str) -> list[str]:
        """Extract atomic blocks (paragraphs, code blocks, tables)."""
        blocks = []
        in_code_block = False
        current_block = []

        for line in text.split("\n"):
            if line.strip().startswith("```"):
                if in_code_block:
                    current_block.append(line)
                    blocks.append("\n".join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    if current_block:
                        blocks.append("\n".join(current_block))
                        current_block = []
                    current_block.append(line)
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)
            elif line.strip() == "":
                if current_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
            else:
                current_block.append(line)

        if current_block:
            blocks.append("\n".join(current_block))

        return [b for b in blocks if b.strip()]

    def _add_overlap(self, chunks: list[DocChunk]) -> list[DocChunk]:
        """Add token overlap between consecutive chunks."""
        if len(chunks) <= 1 or self.overlap_tokens <= 0:
            return chunks

        for i in range(1, len(chunks)):
            prev_text = chunks[i - 1].text
            prev_tokens = self.tokenizer.encode(prev_text)

            if len(prev_tokens) > self.overlap_tokens:
                overlap_text = self.tokenizer.decode(
                    prev_tokens[-self.overlap_tokens:]
                )
                chunks[i].text = f"...{overlap_text}\n\n{chunks[i].text}"
                chunks[i].token_count = self._count_tokens(chunks[i].text)

        return chunks

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))

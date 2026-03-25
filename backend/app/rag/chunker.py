from __future__ import annotations

import re
from typing import Any

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


class TextChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )

    def split(self, text: str) -> list[dict[str, Any]]:
        if not text or not text.strip():
            return []
        chunks = self.splitter.split_text(text)
        return [{"text": chunk, "metadata": {}} for chunk in chunks]


class MarkdownChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
            strip_headers=False,
        )
        self.body_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )

    def split(self, text: str) -> list[dict[str, Any]]:
        if not text or not text.strip():
            return []
        header_docs = self.header_splitter.split_text(text)
        results: list[dict[str, Any]] = []
        for doc in header_docs:
            subchunks = self.body_splitter.split_text(doc.page_content)
            for subchunk_index, subchunk in enumerate(subchunks):
                results.append(
                    {
                        "text": subchunk,
                        "metadata": {**doc.metadata, "subchunk_index": subchunk_index},
                    }
                )
        return results


class SemanticChunker:
    """Chunker semántico con separación por contexto lógico y overlap inteligente."""

    def __init__(
        self,
        *,
        chunk_size: int,
        overlap_min: int,
        overlap_max: int,
    ) -> None:
        self.chunk_size = chunk_size
        self.overlap_min = overlap_min
        self.overlap_max = overlap_max
        self.section_splitter = re.compile(r"\n(?=(?:#{1,6}\s|[A-Z][A-Z0-9 _-]{3,}:))")
        self.sentence_splitter = re.compile(r"(?<=[.!?])\s+")

    def _compute_overlap(self, section_text: str) -> int:
        density = section_text.count(".") + section_text.count(":")
        dynamic = self.overlap_min + int(density * 0.8)
        return max(self.overlap_min, min(self.overlap_max, dynamic))

    def _split_section(self, section_text: str, base_metadata: dict[str, Any]) -> list[dict[str, Any]]:
        if len(section_text) <= self.chunk_size:
            return [{"text": section_text, "metadata": base_metadata}]

        sentences = self.sentence_splitter.split(section_text)
        chunks: list[dict[str, Any]] = []
        current: list[str] = []
        current_size = 0
        overlap = self._compute_overlap(section_text)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence_len = len(sentence)
            if current_size + sentence_len > self.chunk_size and current:
                chunk_text = " ".join(current)
                chunks.append({"text": chunk_text, "metadata": {**base_metadata, "overlap": overlap}})
                tail = chunk_text[-overlap:]
                current = [tail, sentence]
                current_size = len(tail) + sentence_len
            else:
                current.append(sentence)
                current_size += sentence_len

        if current:
            chunks.append({"text": " ".join(current), "metadata": {**base_metadata, "overlap": overlap}})
        return chunks

    def split(self, text: str) -> list[dict[str, Any]]:
        if not text or not text.strip():
            return []
        sections = [s.strip() for s in self.section_splitter.split(text) if s.strip()]
        if not sections:
            sections = [text.strip()]

        chunks: list[dict[str, Any]] = []
        for logical_context_index, section in enumerate(sections):
            base_metadata = {"logical_context_index": logical_context_index}
            chunks.extend(self._split_section(section, base_metadata))
        return chunks

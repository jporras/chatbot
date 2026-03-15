from __future__ import annotations

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
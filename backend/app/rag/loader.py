from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_community.document_loaders import PyPDFLoader


class DocumentLoader:
    def load(self, path: str) -> list[dict[str, Any]]:
        suffix = Path(path).suffix.lower()

        if suffix == ".pdf":
            return self._load_pdf(path)
        if suffix in {".md", ".txt"}:
            content = Path(path).read_text(encoding="utf-8")
            return [{
                "text": content,
                "metadata": {
                    "source": path,
                    "filename": Path(path).name,
                },
            }]

        raise ValueError(f"Unsupported file type: {suffix}")

    def _load_pdf(self, path: str) -> list[dict[str, Any]]:
        loader = PyPDFLoader(path, mode="page")
        docs = loader.load()
        return [
            {
                "text": doc.page_content,
                "metadata": {
                    **doc.metadata,
                    "source": path,
                    "filename": Path(path).name,
                },
            }
            for doc in docs
            if doc.page_content and doc.page_content.strip()
        ]
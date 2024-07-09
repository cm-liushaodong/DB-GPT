"""PDF Knowledge."""
from typing import Any, Dict, List, Optional, Union

from dbgpt.core import Document
from dbgpt.rag.knowledge.base import (
    ChunkStrategy,
    DocumentType,
    Knowledge,
    KnowledgeType,
)


class PDFKnowledge(Knowledge):
    """PDF Knowledge."""

    def __init__(
        self,
        file_path: Optional[str] = None,
        knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT,
        loader: Optional[Any] = None,
        language: Optional[str] = "zh",
        metadata: Optional[Dict[str, Union[str, List[str]]]] = None,
        **kwargs: Any,
    ) -> None:
        """Create PDF Knowledge with Knowledge arguments.

        Args:
            file_path(str,  optional): file path
            knowledge_type(KnowledgeType, optional): knowledge type
            loader(Any, optional): loader
            language(str, optional): language
        """
        super().__init__(
            path=file_path,
            knowledge_type=knowledge_type,
            data_loader=loader,
            metadata=metadata,
            **kwargs,
        )
        self._language = language

    def _load(self) -> List[Document]:
        """Load pdf document from loader."""
        if self._loader:
            documents = self._loader.load()
        else:
            import re
            import fitz  # PyMuPDF

            pages_list = []
            documents = []
            if not self._path:
                raise ValueError("file path is required")

            pdf_document = fitz.open(self._path)

            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                clip = 50
                crop = fitz.Rect(0, clip, page.rect.width, page.rect.height - clip)
                text = page.get_text(clip=crop)
                pages_list.append((text, page_num))

            # cleaned_pages = []
            en_lines = []
            cn_lines = []
            cleaned_lines = []
            for page, page_num in pages_list:
                lines = page.splitlines()
                for line in lines:
                    # 对分割后的前半句进行判断：是否一半以上都是英文
                    if len(re.findall(r'[a-zA-Z]', line)) > len(line) / 2:
                        en_lines.append(line.strip())
                    else:
                        cn_lines.append(line.strip())
                cleaned_lines = en_lines + cn_lines
                page = " ".join(cleaned_lines)
                # cleaned_pages.append(page)

                metadata = {"source": self._path, "page": page_num}
                if self._metadata:
                    metadata.update(self._metadata)  # type: ignore

                # text = "\f".join(cleaned_pages)
                document = Document(content=page, metadata=metadata)
                documents.append(document)
            return documents
        return [Document.langchain2doc(lc_document) for lc_document in documents]

    @classmethod
    def support_chunk_strategy(cls) -> List[ChunkStrategy]:
        """Return support chunk strategy."""
        return [
            ChunkStrategy.CHUNK_BY_SIZE,
            ChunkStrategy.CHUNK_BY_PAGE,
            ChunkStrategy.CHUNK_BY_SEPARATOR,
        ]

    @classmethod
    def default_chunk_strategy(cls) -> ChunkStrategy:
        """Return default chunk strategy."""
        return ChunkStrategy.CHUNK_BY_SIZE

    @classmethod
    def type(cls) -> KnowledgeType:
        """Return knowledge type."""
        return KnowledgeType.DOCUMENT

    @classmethod
    def document_type(cls) -> DocumentType:
        """Document type of PDF."""
        return DocumentType.PDF

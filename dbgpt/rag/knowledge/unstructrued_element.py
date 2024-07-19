from typing import Iterable, Optional

from unstructured.documents.elements import Element, ElementMetadata, ElementType


class CleanedElement(Element):
    def __init__(self, element_id, element_type, text, metadata):
        super().__init__(element_id, metadata=metadata)
        self.element_id = element_id
        self.type = element_type
        self.text = text
        self.metadata = metadata

    def to_dict(self):
        return {
            "element_id": self.element_id,
            "type": None if self.type is None else self.type,
            "text": None if self.text is None else self.text,
            "metadata": None if self.metadata is None else self.metadata.to_dict(),
        }


class CleanedMetadata(ElementMetadata):
    def __init__(self, filename, page_number):
        super().__init__(filename=filename, page_number=page_number)
        self.filename = filename
        self.page_number = page_number

    def to_dict(self):
        return {
            "filename": None if self.filename is None else self.filename,
            "page_number": None if self.page_number is None else self.page_number,
        }


def custom_chunk_elements(
    elements: Iterable[CleanedElement],
    combine_text_under_n_chars: Optional[int] = 300,
    max_characters: Optional[int] = None,
    overlap: Optional[int] = None,
):
    chunks = []
    chunk = ""
    title_index = 0

    for index, element in enumerate(elements):
        if element.type in [ElementType.TITLE]:
            if chunk:
                chunks.append(chunk)
                chunk = ""
            chunks.append(element.text)
            title_index = len(chunks) - 1
        elif element.type in [ElementType.TABLE]:
            if chunk:
                chunks.append(chunk)
                chunk = ""

            table_text = " ".join(chunks[title_index:])
            table_text += " " + element.text

            del chunks[title_index:]
            chunks.append(table_text)
        elif len(element.text) > max_characters:
            if chunk:
                chunks.append(chunk)
                chunk = ""
            chunks.extend(split_element(element, max_characters, overlap))
        elif len(chunk) + len(element.text) > max_characters:
            chunks.append(chunk)
            chunk = ""
        else:
            chunk += " " + element.text
            if index == len(list(elements)) - 1 and chunk:
                chunks.append(chunk)
    if combine_text_under_n_chars:
        chunks = combine_short_text(chunks, combine_text_under_n_chars, max_characters)

    return chunks


def split_element(element: CleanedElement, max_characters: int, overlap: int):
    start = 0
    end = len(element.text)
    cursor = start

    splits = []

    while cursor + max_characters < end:
        splits.append(element.text[cursor : cursor + max_characters])
        cursor += max_characters - overlap

    if cursor < end:
        splits.append(element.text[cursor:])

    return splits


def combine_short_text(
    chunks: Iterable[str], combine_text_under_n_chars: int, max_characters: int
):
    result_chunks = []
    current_chunk = ""

    for chunk in chunks:
        if len(chunk) + len(current_chunk) <= max_characters:
            if len(current_chunk) < combine_text_under_n_chars:
                current_chunk += " " + chunk
            else:
                result_chunks.append(current_chunk)
                current_chunk = chunk
        else:
            if current_chunk:
                result_chunks.append(current_chunk)
            current_chunk = chunk

    if current_chunk:
        result_chunks.append(current_chunk)

    return result_chunks

from unstructured.documents.elements import Element, ElementMetadata


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

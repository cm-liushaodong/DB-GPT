from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.cleaners.core import clean
import opencc
import json
from unstructured.documents.elements import ElementType
from dbgpt.rag.knowledge.base import (
    ChunkStrategy,
    DocumentType,
    Knowledge,
    KnowledgeType,
)
from dbgpt.core import Document

from dbgpt.rag.knowledge.unstructrued_element import CleanedMetadata, CleanedElement

path = "/Users/liushaodong/Desktop/pdf_documents/多页文档_文字混表格.pdf"

# elements = partition(path,strategy="hi_res",hi_res_model_name="yolox")

# print("\n\n".join([str(el) for el in elements]))

pages = []
page = []
documents = []

elements = partition_pdf(path, strategy='hi_res', hi_res_model_name='yolox',
                        infer_table_structure=True,
                        form_extraction_skip_tables=[], languages=['chi_tra', 'chi_sim', 'eng'],
                        include_page_breaks=True)

# print("\n\n".join([str(el) for el in elements]))


converter = opencc.OpenCC('t2s')

for element in elements:
    ele_json = json.loads(json.dumps(element.to_dict(), indent=2))
    print("xxxxxxxxxx")
    print(ele_json)
    if ele_json.get('type') == ElementType.PAGE_BREAK and page:
        pages.append(page)
        page = []
    else:
        element_id = ele_json.get('element_id')
        element_type = ele_json.get('type')
        if ele_json.get('type') in [ElementType.TABLE] and ele_json.get('metadata').get('text_as_html'):
            element_text = ele_json.get('metadata').get('text_as_html')
        else:
            element_text = ele_json.get('text')
        element_text = clean(element_text)
        # 繁体中文转简体中文，后面需要对语言类型(用户输入、chunk的语言进行统一)
        element_text = converter.convert(element_text)
        page_number = ele_json.get('metadata').get('page_number')
        file_name = ele_json.get('metadata').get('filename')

        metadata = CleanedMetadata(file_name, page_number)
        cleaned_element = CleanedElement(element_id, element_type, element_text, metadata)

        page.append(cleaned_element.to_dict())

if page:
    pages.append(page)

for index, page in enumerate(pages):
    page_str = json.dumps(page, indent=2)
    metadata = {"source": path, "page": index}
    document = Document(content=page_str, metadata=metadata)
    documents.append(document)
    print("xxxxxxxxxx")
    # print(document)

import os
from typing import List

from InfoGrep_BackendSDK.service_endpoints import vectordb_host
from utils import convert_collection_name
from langchain_community.vectorstores import Milvus

class Citation:
    def __init__(self, page: int, textContent: str, file: str):
        self.page = page
        self.textContent = textContent
        self.file = file

def vector_search(query: str, embedding_model: str, embedding_func, k: int) -> tuple[List, List]:
    vector_store = Milvus(
        collection_name=convert_collection_name(embedding_model),
        embedding_function=embedding_func,
        connection_args={
            "address": vectordb_host,
            "user": os.environ.get("INFOGREP_MILVUS_USER"),
            "password": os.environ.get("INFOGREP_MILVUS_PASSWORD")
        }
    )
    # Find the closest few documents
    docs = vector_store.similarity_search(query, k) # TODO: filter by chatroom uuid
    citations = [Citation(page=doc.metadata['page'], textContent=doc.page_content, file=doc.metadata['source']) for doc in docs]
    return citations
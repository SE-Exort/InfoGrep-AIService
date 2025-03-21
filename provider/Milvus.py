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

def vector_search(query: str, chatroom_uuid: str, embedding_model: str, embedding_func, k: int) -> tuple[List, List]:
    vector_store = Milvus(
        collection_name=convert_collection_name(embedding_model),
        embedding_function=embedding_func,
        connection_args={
            "address": vectordb_host,
            "user": os.environ.get("INFOGREP_MILVUS_USER"),
            "password": os.environ.get("INFOGREP_MILVUS_PASSWORD")
        }
    )
    
    # Find the closest few documents in the chatroom
    docs = vector_store.similarity_search(query, k, expr=f'chatroom == "{chatroom_uuid}"')
    citations = [Citation(page=doc.metadata['page'], textContent=doc.page_content, file=doc.metadata['source']) for doc in docs]
    return citations

def remove_embeddings(chatroom_uuid: str, embedding_model: str, embedding_func, file_uuid: str):
    vector_store = Milvus(
        collection_name=convert_collection_name(embedding_model),
        embedding_function=embedding_func,
        connection_args={
            "address": vectordb_host,
            "user": os.environ.get("INFOGREP_MILVUS_USER"),
            "password": os.environ.get("INFOGREP_MILVUS_PASSWORD")
        }
    )

    print(f'chatroom == "{chatroom_uuid}" && source == "{file_uuid}"')
    vector_store.delete(expr=f'chatroom == "{chatroom_uuid}" && source == "{file_uuid}"')
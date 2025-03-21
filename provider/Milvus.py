import os
from typing import List

from InfoGrep_BackendSDK.service_endpoints import vectordb_host
from provider.Ollama import Ollama
from utils import convert_collection_name
from langchain_community.vectorstores import Milvus
from langchain_core.documents import Document

class Citation:
    def __init__(self, page: int, textContent: str, file: str):
        self.page = page
        self.textContent = textContent
        self.file = file

def get_vector_store(embedding_model: str) -> Milvus:
    # Assume an Ollama + Milvus combination
    embeddings = Ollama().embedding(embedding_model)
    return Milvus(embedding_function=embeddings, collection_name=convert_collection_name(embedding_model), auto_id=True, connection_args={
            "address": vectordb_host,
            "user": os.environ.get("INFOGREP_MILVUS_USER"),
            "password": os.environ.get("INFOGREP_MILVUS_PASSWORD")
        })

def add_embeddings(embedding_model: str, documents: List[Document]) -> None:
    get_vector_store(embedding_model).add_documents(documents)

# Find the closest few documents in the chatroom
def vector_search(query: str, chatroom_uuid: str, embedding_model: str, k: int) -> List[Citation]:
    docs = get_vector_store(embedding_model).similarity_search(query, k, expr=f'chatroom == "{chatroom_uuid}"')
    citations = [Citation(page=doc.metadata['page'], textContent=doc.page_content, file=doc.metadata['source']) for doc in docs]
    return citations

def remove_embeddings(chatroom_uuid: str, embedding_model: str, file_uuid: str):
    print(f'chatroom == "{chatroom_uuid}" && source == "{file_uuid}"')
    get_vector_store(embedding_model).delete(expr=f'chatroom == "{chatroom_uuid}" && source == "{file_uuid}"')
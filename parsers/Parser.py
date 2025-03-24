from abc import ABC, abstractmethod
from os import remove
from typing import List

from InfoGrep_BackendSDK import fms_api
from utils import convert_collection_name
from langchain_core.documents import Document

# Only keep standard metadata otherwise insertion may fail
METADATA_WHITELIST = ['page', 'source', 'chatroom']
def clean_metadata(metadata_items):
    cleaned_metadata = dict()
    for k,v in metadata_items:
        if k in METADATA_WHITELIST:
            cleaned_metadata.update({convert_collection_name(k): v})
    return cleaned_metadata

class Parser(ABC):
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        remove(self.file_uuid)
    
    def __init__(self, chatroom_uuid: str, file_uuid: str, cookie: str, embedding_model: str):
        self.chatroom_uuid = chatroom_uuid
        self.embedding_model = embedding_model
        self.file_uuid = file_uuid
        self.cookie = cookie

        file = fms_api.fms_getFile(self.chatroom_uuid, self.file_uuid, self.cookie)
        with open(self.file_uuid, "wb") as files:
            files.write(file.content)

    def parse(self) -> List[Document]:
        pages = []
        for page in self.get_loader().load():
            # Metadata names are probably not compatible with Milvus naming requirements, clean them beforehand
            page.metadata["chatroom"] = self.chatroom_uuid
            if 'page' not in page.metadata:
                page.metadata["page"] = 0
            page.metadata = clean_metadata(page.metadata.items())
            page.page_content = page.page_content[:65000]
            pages.append(page)
            print(page)
        return pages
    
    @abstractmethod
    def get_loader(self):
        pass
    
    @abstractmethod
    def fileType():
        pass

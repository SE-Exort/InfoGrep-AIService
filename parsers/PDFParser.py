from os import remove
from langchain_ollama import OllamaEmbeddings
from parsers.Parser import Parser

import uuid, os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Milvus

from utils import convert_collection_name
from InfoGrep_BackendSDK.service_endpoints import vectordb_host

# Only keep standard metadata otherwise insertion may fail
METADATA_WHITELIST = ['page', 'source', 'chatroom']
def clean_metadata(metadata_items):
    cleaned_metadata = dict()
    for k,v in metadata_items:
        if k in METADATA_WHITELIST:
            cleaned_metadata.update({convert_collection_name(k): v})
    return cleaned_metadata

class PDFParser(Parser):
    def startParsing(self):
        file = self.getFile()
        tempFileName = str(uuid.uuid4()) + ".pdf"
        with open(tempFileName, "wb") as files:
            files.write(file.content)
        
        # lang chain parsing
        loader = PyPDFLoader(tempFileName)
        pages = []
        for page in loader.load():
            # Metadata names are probably not compatible with Milvus naming requirements, clean them beforehand
            page.metadata["chatroom"] = self.ChatRoomUUID
            page.metadata = clean_metadata(page.metadata.items())
            pages.append(page)

        embeddings = OllamaEmbeddings(model=self.EmbeddingModel)
        # put into milvus collection corresponding to the chatroom embedding model
        vector_store = Milvus(embedding_function=embeddings, collection_name=convert_collection_name(self.EmbeddingModel), auto_id=True, connection_args={
                "address": vectordb_host,
                "user": os.environ.get("INFOGREP_MILVUS_USER"),
                "password": os.environ.get("INFOGREP_MILVUS_PASSWORD")
            })
        vector_store.add_documents(pages)
        
        remove(tempFileName)
        return

    def cancelParsing(self):
        self.canceled = True
        return

    def getParsingStatus(self):
        return

    def fileType():
        return "PDF"

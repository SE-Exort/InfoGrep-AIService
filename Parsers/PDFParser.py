from langchain_ollama import OllamaEmbeddings
from Parsers.Parser import Parser

import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Milvus

from utils import convert_collection_name

class PDFParser(Parser):
    def startParsing(self):
        print("stared parsing pdf")
        file = self.getFile()
        tempFileName = str(uuid.uuid4())
        with open(tempFileName+".pdf", "wb") as files:
            files.write(file.content)
        print("temp file written as ", tempFileName, ".pdf")
        # lang chain parsing
        loader = PyPDFLoader(tempFileName + ".pdf")
        pages = []
        for page in loader.load():
            cleaned_metadata = dict()
            for k,v in page.metadata.items():
                cleaned_metadata.update({convert_collection_name(k): v})
            page.metadata = cleaned_metadata
            page.metadata["chatroom"] = self.ChatRoomUUID
            pages.append(page)
            print(page)

        embeddings = OllamaEmbeddings(model=self.EmbeddingModel)

        # put into milvus collection corresponding to the chatroom embedding model
        vector_store = Milvus(embedding_function=embeddings, collection_name=convert_collection_name(self.EmbeddingModel), auto_id=True)
        added_ids = vector_store.add_documents(pages)
        print(added_ids)
        # TODO: remove the file that we created
        return

    def cancelParsing(self):
        self.canceled = True
        return

    def getParsingStatus(self):
        return

    def fileType():
        return "PDF"

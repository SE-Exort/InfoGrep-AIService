from Parsers.Parser import Parser

import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Milvus

class PDFParser(Parser):
    def startParsing(self):
        file = self.getFile()
        tempFileName = str(uuid.uuid4())
        with open(tempFileName+".pdf", "wb") as files:
            files.write(file.content)
        
        # lang chain parsing
        loader = PyPDFLoader(tempFileName + ".pdf")
        documents = loader.load_and_split()

        for doc in documents:
            doc.metadata["chatroom"] = self.ChatRoomUUID

        model_name = "BAAI/bge-small-en"
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}
        hf = HuggingFaceBgeEmbeddings(
            model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
        )

        Milvus.from_documents(documents, hf, partition_key_field="chatroom")
        # TODO: remove the file that we created?
        return;

    def cancelParsing(self):
        self.canceled = True;
        return;

    def getParsingStatus(self):
        return;

    def fileType():
        return "PDF"

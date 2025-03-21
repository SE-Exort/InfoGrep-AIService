from parsers.Parser import Parser

from langchain_community.document_loaders import PyPDFLoader

class PDFParser(Parser):
    def get_loader(self):
        return PyPDFLoader(self.file_uuid)

    def fileType():
        return "PDF"

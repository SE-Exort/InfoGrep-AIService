from typing import List

from parsers.Parser import Parser
from langchain_community.document_loaders.text import TextLoader
from langchain_core.documents import Document

class TxtParser(Parser):
    def get_loader(self):
        return TextLoader(self.file_uuid)

    def fileType():
        return "TXT"

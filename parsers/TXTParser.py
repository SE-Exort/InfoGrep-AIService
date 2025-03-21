from typing import List

from parsers.Parser import Parser
from langchain_community.document_loaders.parsers.txt import TextParser
from langchain_core.documents import Document

class TxtParser(Parser):
    def parse(self) -> List[Document]:
        return TextParser(self.file_uuid)

    def fileType():
        return "TXT"

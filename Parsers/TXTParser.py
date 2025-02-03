from Parsers.Parser import Parser
import re

class TXTParser(Parser):
    def __init__(self):
        self.canceled = False
        self.sentences = []

    def startParsing(self):
        file = self.getFile()
        with open(file, 'r', encoding='utf-8') as file:
            text = file.read()
            self.sentences = self.parse_by_sentence(text)
        return;

    def cancelParsing(self):
        self.canceled = True;
        return;

    def getParsingStatus(self):
        return;

    def fileType():
        return "TXT"
    
    def parse_by_sentence(self, text):
        sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
        sentences = sentence_endings.split(text)
        return sentences

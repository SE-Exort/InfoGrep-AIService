from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document

class Integration(ABC):
    def __init__(self, chatroom_uuid: str, config: dict, cookie: str):
        self.chatroom_uuid = chatroom_uuid
        self.config = config

    @abstractmethod
    def parse(self) -> List[Document]:
        pass
from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel
from InfoGrep_BackendSDK.service_endpoints import vectordb_host

class Citation:
    def __init__(self, page: int, textContent: str, file: str):
        self.page = page
        self.textContent = textContent
        self.file = file

class Response:
    def __init__(self, response: str, thinking: str, citations: List[Citation]):
        self.response = response
        self.thinking = thinking
        self.citations = citations

class MessageHistory(BaseModel):
    message: str
    is_user: bool

class AIWrapper(ABC):
    def __init__(self, chatroom_uuid, cookie):
        self.ChatRoomUUID = chatroom_uuid
        self.Cookie = cookie
        self.milvus_address = vectordb_host

    @abstractmethod
    def summarize(self, history: List[MessageHistory], historyembedding_model: str, chat_model: str) -> Response:
        pass

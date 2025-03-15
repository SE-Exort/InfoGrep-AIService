from abc import ABC, abstractmethod
from InfoGrep_BackendSDK.service_endpoints import vectordb_host

class AIWrapper(ABC):

    def __init__(self, chatroom_uuid, cookie):
        self.ChatRoomUUID = chatroom_uuid
        self.Cookie = cookie
        self.milvus_address = vectordb_host

    @abstractmethod
    def summarize(self, embedding_model: str, chat_model: str) -> str:
        pass

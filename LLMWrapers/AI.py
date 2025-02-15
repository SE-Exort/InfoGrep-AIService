from abc import ABC, abstractmethod
from InfoGrep_BackendSDK.service_endpoints import vectordb_host

class AIWrapper(ABC):

    def __init__(self, chatroom_uuid, cookie):
        self.ChatRoomUUID = chatroom_uuid;
        self.Cookie = cookie;
        self.Collection = 'test'
        self.milvus_address = vectordb_host

    @abstractmethod
    def summarize(self, text) -> str:
        pass;

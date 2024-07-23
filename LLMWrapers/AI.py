from abc import ABC, abstractmethod

from InfoGrep_BackendSDK import vectordb_api

class AIWrapper(ABC):

    def __init__(self, chatroom_uuid, cookie):
        self.ChatRoomUUID = chatroom_uuid;
        self.Cookie = cookie;
        self.Collection = 'test'
    
    def getVectors(self, text):
        return vectordb_api.vectordb_search(collection=self.Collection,vector=text,chatroom_uuid=self.ChatRoomUUID, cookie=self.Cookie, args=None);

    @abstractmethod
    def summarize(self, text) -> str:
        pass;


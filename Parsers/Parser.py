from abc import ABC, abstractmethod

from InfoGrep_BackendSDK import fms_api

class Parser(ABC):

    def __init__(self, chatroom_uuid, file_uuid, cookie):
        self.ChatRoomUUID = chatroom_uuid;
        self.FileUUID = file_uuid;
        self.Cookie = cookie;
        self.canceled = False;

    def getFile(self):
        return fms_api.fms_getFile(self.ChatRoomUUID, self.FileUUID, self.Cookie);

    @abstractmethod
    def startParsing(self):
        pass;

    @abstractmethod
    def cancelParsing(self):
        pass;

    @abstractmethod
    def getParsingStatus(self):
        pass;
    
    @abstractmethod
    def fileType():
        pass

    def getChatRoomUUID(self):
        return self.ChatRoomUUID;
    
    def getFileUUID(self):
        return self.FileUUID;

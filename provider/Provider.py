from abc import ABC, abstractmethod

class Provider(ABC):
    @abstractmethod
    def llm(self, chat_model: str):
        pass

    @abstractmethod
    def embedding(self, embedding_model: str):
        pass
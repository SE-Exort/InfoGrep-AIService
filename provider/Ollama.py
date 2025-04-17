from provider.Provider import Provider
from InfoGrep_BackendSDK.service_endpoints import ollama_service_host

from langchain_ollama import OllamaEmbeddings

from langchain_ollama.llms import OllamaLLM

class Ollama(Provider):
    def embedding(self, embedding_model: str):
        return OllamaEmbeddings(model=embedding_model, base_url=ollama_service_host)

    def llm(self, chat_model: str):
        return OllamaLLM(model=chat_model, base_url=ollama_service_host)
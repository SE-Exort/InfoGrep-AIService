from LLMWrapers.AI import AIWrapper
from InfoGrep_BackendSDK.service_endpoints import ollama_service_host
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Milvus
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

from utils import convert_collection_name

class Ollama(AIWrapper):
    def summarize(self, query: str, embedding_model: str, chat_model: str) -> str:
        embeddings = OllamaEmbeddings(model=embedding_model)
        print("Using collection", convert_collection_name(embedding_model), "for query ", query, "and chatroom", self.ChatRoomUUID)
        # Find the closest few documents
        vector_store = Milvus(
            collection_name=convert_collection_name(embedding_model),
            embedding_function=embeddings,
            connection_args={
                "address": self.milvus_address,
                "user": os.environ.get("INFOGREP_MILVUS_USER"),
                "password": os.environ.get("INFOGREP_MILVUS_PASSWORD")
            }
        )
        docs = vector_store.similarity_search(query, k=3) # TODO: filter by chatroom uuid
        print("similarity search by vector: ", docs)

        template = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant to an enterprise user. Answer the query in a polite and informative tone."),
                ("human", "{user_input}"),
            ] if len(docs) == 0 else [
                ("system", "You are a helpful assistant to an enterprise user. Answer the query using the provided information."),
                ("system", "" + docs[0].page_content),
                ("human", "{user_input}"),
            ])

        model = OllamaLLM(model=chat_model, base_url=ollama_service_host)

        chain = template | model

        ai_msg = chain.invoke({"user_input": query})

        return ai_msg
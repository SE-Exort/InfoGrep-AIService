from LLMWrapers.AI import AIWrapper
from InfoGrep_BackendSDK.service_endpoints import ollama_service_host
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Milvus
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

class Ollama(AIWrapper):
    def summarize(self, query: str, embedding_model: str, chat_model: str) -> str:
        embeddings = OllamaEmbeddings(model=embedding_model)

        # Find the closest few documents
        vector_store = Milvus(
            embedding_function=embeddings, 
            connection_args={
                "address": self.milvus_address,
                "user": os.environ.get("INFOGREP_MILVUS_USER"),
                "password": os.environ.get("INFOGREP_MILVUS_PASSWORD")
            }
        )
        query_embedding = embeddings.embed_query(query)
        docs = vector_store.similarity_search_by_vector(query_embedding)

        template = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant to an enterprise user. Answer the query in a polite and informative tone."),
                ("human", "{user_input}"),
            ] if len(docs) == 0 else [
                ("system", "You are a helpful assistant to an enterprise user. Answer the query using the provided information."),
                ("sytem", "" + docs[0].page_content),
                ("human", "{user_input}"),
            ])

        model = OllamaLLM(model=chat_model, base_url=ollama_service_host)

        chain = template | model

        ai_msg = chain.invoke({"user_input": query})
        print("***")
        print(ai_msg)

        return ai_msg
import re
from typing import List
from Endpoints import MessageHistory
from LLMWrapers.AI import AIWrapper, Citation, Response
from InfoGrep_BackendSDK.service_endpoints import ollama_service_host
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Milvus
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

from utils import convert_collection_name

class Ollama(AIWrapper):
    def summarize(self, history: List[MessageHistory], query: str, embedding_model: str, chat_model: str) -> Response:
        embeddings = OllamaEmbeddings(model=embedding_model)
        vector_store = Milvus(
            collection_name=convert_collection_name(embedding_model),
            embedding_function=embeddings,
            connection_args={
                "address": self.milvus_address,
                "user": os.environ.get("INFOGREP_MILVUS_USER"),
                "password": os.environ.get("INFOGREP_MILVUS_PASSWORD")
            }
        )
        # Find the closest few documents
        docs = vector_store.similarity_search(query, k=3) # TODO: filter by chatroom uuid
        citations = [Citation(page=doc.metadata['page'], textContent=doc.page_content, file=doc.metadata['source']) for doc in docs]

        messages = [
                ("system", "You are a helpful assistant to an enterprise user. Answer the user question in a polite and helpful tone."),
                *([("system", "Only use the provided information in your response.")] if len(docs) else []),
                *[("system", d.page_content) for d in docs],
                *[("human" if h.is_user else "system", h.message) for h in history],
                ("human", "{user_input}")
            ]
        template = ChatPromptTemplate.from_messages(messages)
        print(messages)

        model = OllamaLLM(model=chat_model, base_url=ollama_service_host)
        chain = template | model
        ai_msg = chain.invoke({"user_input": query})

        thoughts = re.findall(r"<think>.*<\/think>", ai_msg, re.DOTALL)
        response_without_thoughts = re.sub(r"<think>.*<\/think>", "", ai_msg, flags=re.DOTALL)
        return Response(response=response_without_thoughts, thinking=thoughts[0] if len(thoughts) > 0 else None, citations=citations)
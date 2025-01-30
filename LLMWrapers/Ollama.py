from langchain_huggingface import HuggingFaceEmbeddings
from LLMWrapers.AI import AIWrapper

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Milvus

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import ChatOllama

class Ollama(AIWrapper):
    def summarize(self, query):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

        # Find the closest few documents
        vector_store = Milvus(embedding_function=embeddings)
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

        model = OllamaLLM(model="deepseek-r1")

        chain = template | model

        ai_msg = chain.invoke({"user_input": query})
        print("***")
        print(ai_msg)

        return ai_msg
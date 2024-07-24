from LLMWrapers.AI import AIWrapper

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Milvus

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

class Local(AIWrapper):
    def summarize(self, query):
        model_name = "BAAI/bge-small-en"
        model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": True}
        hf = HuggingFaceBgeEmbeddings(
            model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
        )

        embedding_vector = hf.embed_query(query)
        docs = Milvus(hf).similarity_search_by_vector(embedding_vector)

        template = ChatPromptTemplate.from_messages([
                ("system", "Answer the user question."),
                ("human", "Here is information from my course: " + docs[0].page_content),
                ("human", "{user_input}"),
            ])

        model = OllamaLLM(model="llama3")

        chain = template | model

        ai_msg = chain.invoke({"user_input": query})
        print("***")
        print(ai_msg)

        return ai_msg
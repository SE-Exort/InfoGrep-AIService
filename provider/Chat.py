import re
from typing import List

from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from provider.Milvus import Citation

class Response:
    def __init__(self, response: str, thinking: str, citations: List[Citation]):
        self.response = response
        self.thinking = thinking
        self.citations = citations

class MessageHistory(BaseModel):
    message: str
    is_user: bool

def chat(citations: List[Citation], history: List[MessageHistory], query: str, chat_llm) -> Response:
    messages = [
            ("system", "You are a helpful assistant to an enterprise user. Answer the user question in a polite and helpful tone."),
            *([("system", "Only use the provided information in your response.")] if len(citations) else []),
            *[("system", c.textContent) for c in citations],
            *[("human" if h.is_user else "system", h.message) for h in history],
            ("human", "{user_input}")
        ]
    template = ChatPromptTemplate.from_messages(messages)
    print("Chat prompt and history", messages)

    chain = template | chat_llm
    ai_msg = chain.invoke({"user_input": query})
    print("AI Response: ", ai_msg)

    thoughts = re.findall(r"<think>.*<\/think>", ai_msg, re.DOTALL)
    response_without_thoughts = re.sub(r"<think>.*<\/think>", "", ai_msg, flags=re.DOTALL).replace('<think>', '').replace('</think>', '').strip()
    return Response(response=response_without_thoughts, thinking=thoughts[0] if len(thoughts) > 0 else None, citations=citations)
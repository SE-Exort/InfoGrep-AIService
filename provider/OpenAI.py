from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from provider.Provider import Provider
from sqlalchemy.orm import Session

class OpenAI(Provider):
    def embedding(self, embedding_model: str, db: Session):
        p = db.query(Provider).where(Provider.provider=='openai').first()
        s = p.settings
        return OpenAIEmbeddings(model=embedding_model, api_key=s['key'])

    def llm(self, chat_model: str, db: Session):
        p = db.query(Provider).where(Provider.provider=='openai').first()
        s = p.settings
        return ChatOpenAI(
            model=chat_model,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=s['key'],
        )
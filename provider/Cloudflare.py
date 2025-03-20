from sqlalchemy.orm import Session
from langchain_community.llms.cloudflare_workersai import CloudflareWorkersAI

from db import Provider
from provider.Provider import Provider as BaseProvider

class Cloudflare(BaseProvider):
    def embedding(self, embedding_model: str):
        pass

    def llm(self, chat_model: str, db: Session):
        p = db.query(Provider).where(Provider.provider=='cloudflare').first()
        s = p.settings
        return CloudflareWorkersAI(account_id=s['account_id'], api_token=s['api_token'], model=chat_model)
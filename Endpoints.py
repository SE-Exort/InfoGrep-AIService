from os import environ
from typing import List
from fastapi import APIRouter, Body, Depends, Request
from fastapi.openapi.docs import get_swagger_ui_html

from provider.Chat import MessageHistory, chat
from provider.Cloudflare import Cloudflare
from provider.Milvus import remove_embeddings, vector_search
from provider.Ollama import Ollama
from provider.OpenAI import OpenAI
from utils import download_model
from InfoGrep_BackendSDK import authentication_sdk, room_sdk
from parsers import PDFParser, Parser

from sqlalchemy.orm import Session

from pydantic import BaseModel

from db import ModelType, ModelWhitelist, Provider, get_db
from sqlalchemy.sql import text

router = APIRouter(prefix='/api', tags=["api"])

supportedFileTypes = dict()
# for cls in Parser.Parser.__subclasses__():
#     print(cls.fileType(), cls)
#     supportedFileTypes.update({cls.fileType(): cls})
supportedFileTypes.update({'PDF': PDFParser.PDFParser})

ollama, openai, cf = Ollama(), OpenAI(), Cloudflare()

@router.post('/parse_file')
def post_start_parsing(request: Request, chatroom_uuid, file_uuid, filetype, cookie):
    authentication_sdk.User(cookie, headers=request.headers)
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers)
    room = room_sdk.get_room(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers)

    if filetype not in supportedFileTypes:
        raise Exception(status_code=400, detail=f"Parsing file type {filetype} is not supported")

    try:
        parser: Parser.Parser = supportedFileTypes[filetype](chatroom_uuid=chatroom_uuid, file_uuid=file_uuid, cookie=cookie, chatroom_embedding_model=room['embedding_model'])
        parser.startParsing()
    except Exception as e:
        print("error running parser", e)
        return 500
    return 200

class RemoveEmbeddingParams(BaseModel):
    chatroom_uuid: str
    file_uuid: str
    sessionToken: str

@router.post('/remove_embedding')
def post_remove_embedding(request: Request, p: RemoveEmbeddingParams = Body()):
    authentication_sdk.User(p.sessionToken, headers=request.headers)
    room_sdk.get_userInRoom(chatroom_uuid=p.chatroom_uuid, cookie=p.sessionToken, headers=request.headers)
    room = room_sdk.get_room(chatroom_uuid=p.chatroom_uuid, cookie=p.sessionToken, headers=request.headers)

    remove_embeddings(p.chatroom_uuid, room['embedding_model'], ollama.embedding(room['embedding_model']), p.file_uuid)

@router.get('/file_types')
def get_file_types():
    return list(supportedFileTypes.keys())

class SystemResponseParams(BaseModel):
    chatroom_uuid: str
    history: List[MessageHistory]
    message: str
    sessionToken: str

    embedding_model: str
    embedding_provider: str
    
    chat_model: str
    chat_provider: str


@router.post('/system_response')
def post_system_response(request: Request, p: SystemResponseParams = Body(), db: Session = Depends(get_db)):
    authentication_sdk.User(p.sessionToken, headers=request.headers)
    exists = db.query(db.query(ModelWhitelist).filter(ModelWhitelist.model_type == ModelType.Chat,
                                                      ModelWhitelist.provider==p.chat_provider,
                                                      ModelWhitelist.model==p.chat_model
                                                      ).exists()).scalar()
    if not exists: return {"error": True, "status": "MODEL_NOT_ALLOWED"}

    # assume embedding provider is ollama + milvus
    citations = vector_search(p.message, p.chatroom_uuid, p.embedding_model, ollama.embedding(p.embedding_model), 3)

    # determine chat provider
    chat_llm = None
    if p.chat_provider == "ollama":
        chat_llm = ollama.llm(p.chat_model)
    elif p.chat_provider == "cloudflare":
        chat_llm = cf.llm(p.chat_model, db)
    elif p.chat_provider == "openai":
        chat_llm = openai.llm(p.chat_model, db)
    print("Using chat LLM ", chat_llm, "for request", p)
    return {"error": False, "data": chat(citations=citations, history=p.history, query=p.message, chat_llm=chat_llm)}

@router.get('/models')
def get_models(request: Request, db: Session = Depends(get_db)):
    embedding_models = db.query(ModelWhitelist).filter(ModelWhitelist.model_type == ModelType.Embedding).all()
    chat_models = db.query(ModelWhitelist).filter(ModelWhitelist.model_type == ModelType.Chat).all()
    
    return {
        "error": False,
        "data": {
            "embedding": embedding_models,
            "chat": chat_models
        }
    }

class Model(BaseModel):
    provider: str
    model: str

class ProviderSetting(BaseModel):
    provider: str
    settings: dict

class UpdateModelsParams(BaseModel):
    embedding: List[Model]
    chat: List[Model]

class UpdateProvidersParams(BaseModel):
    providers: List[ProviderSetting]

@router.post('/models')
def update_models(request: Request, sessionToken: str, models: UpdateModelsParams, db: Session = Depends(get_db)):
    user = authentication_sdk.User(sessionToken, {})
    if not user.is_admin: return {"error": True, "status": "USER_NOT_AUTHORIZED"}
    db.execute(text('TRUNCATE TABLE model_whitelist'))

    for m in models.embedding:
        db.add(ModelWhitelist(provider=m.provider, model=m.model, model_type=ModelType.Embedding))
        download_model(m.provider, m.model)
    for m in models.chat:
        db.add(ModelWhitelist(provider=m.provider, model=m.model, model_type=ModelType.Chat))
        download_model(m.provider, m.model)
    db.commit()

    return {"error": False, "status": "MODEL_WHITELIST_UPDATED"}

@router.post('/providers')
def update_models(request: Request, sessionToken: str, providers: UpdateProvidersParams, db: Session = Depends(get_db)):
    user = authentication_sdk.User(sessionToken, {})
    if not user.is_admin: return {"error": True, "status": "USER_NOT_AUTHORIZED"}
    db.execute(text('TRUNCATE TABLE providers'))

    for p in providers.providers:
        db.add(Provider(provider=p.provider, settings=p.settings))
    db.commit()

    return {"error": False, "status": "PROVIDERS_UPDATED"}

# May return sensitive info like API keys, so admin only
@router.get('/providers')
def update_models(request: Request, sessionToken: str, db: Session = Depends(get_db)):
    user = authentication_sdk.User(sessionToken, {})
    if not user.is_admin: return {"error": True, "status": "USER_NOT_AUTHORIZED"}

    return {
        "error": False,
        "data": db.query(Provider).all()
    }

@router.get("/docs")
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/ai/openapi.json",
        title="AI API Doc"
    )
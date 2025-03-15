from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html

from utils import download_model
from InfoGrep_BackendSDK import authentication_sdk, room_sdk
from InfoGrep_BackendSDK.service_endpoints import ollama_service_host
from Parsers.threadpool import ParserThreadPool
from Parsers import PDFParser, Parser

from LLMWrapers import Ollama, OpenAI
from sqlalchemy.orm import Session

from pydantic import BaseModel

from db import ModelType, ModelWhitelist, Provider, get_db
from sqlalchemy.sql import text
import re

router = APIRouter(prefix='/api', tags=["api"])
documentParserThreadPool = ParserThreadPool(10)

supportedFileTypes = dict()
# for cls in Parser.Parser.__subclasses__():
#     print(cls.fileType(), cls)
#     supportedFileTypes.update({cls.fileType(): cls})
supportedFileTypes.update({'PDF': PDFParser.PDFParser})

@router.post('/start_parsing')
async def post_start_parsing(request: Request, chatroom_uuid, file_uuid, filetype, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid']
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers)
    room = room_sdk.get_room(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers)
    try:
        print("getting parser", room, room['embedding_model'][0], supportedFileTypes[filetype])
        parser: Parser.Parser = supportedFileTypes[filetype](chatroom_uuid=chatroom_uuid, file_uuid=file_uuid, cookie=cookie, chatroom_embedding_model=room['embedding_model'][0])
        print('parser constructed', parser)
        parser.startParsing()
    except Exception as e:
        print("error running parser", e)
        return 500

    # documentParserThreadPool.submit_task(parser)
    return 200

@router.post('/cancel_parsing')
def post_cancel_parsing(request: Request, chatroom_uuid, file_uuid, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid']
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers)

    taskkey = documentParserThreadPool.create_taskkey(chatroom_uuid=chatroom_uuid,file_uuid=file_uuid)

    documentParserThreadPool.cancel_task(taskkey=taskkey)
    
    return 200

@router.get('/parsing_status')
def get_parsing_status(request: Request, chatroom_uuid, file_uuid, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid']
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers)
    
    taskkey = documentParserThreadPool.create_taskkey(chatroom_uuid=chatroom_uuid,file_uuid=file_uuid)
    documentParserThreadPool.get_task_status(taskkey=taskkey)
    return 200

@router.get('/file_types')
async def get_file_types():
    return list(supportedFileTypes.keys())

@router.get('/system_response')
async def get_system_response(request: Request, chatroom_uuid, message, cookie, provider, embedding_model, chat_model, db: Session = Depends(get_db)):
    exists = db.query(db.query(ModelWhitelist).filter(ModelWhitelist.model_type == ModelType.Chat, ModelWhitelist.provider==provider, ModelWhitelist.model==chat_model).exists()).scalar()
    if not exists: return {"error": True, "status": "MODEL_NOT_ALLOWED"}

    wrapper = None
    if provider == "ollama":
        wrapper = Ollama.Ollama(chatroom_uuid=chatroom_uuid, cookie=cookie)
    else:
        wrapper = OpenAI.OpenAI(chatroom_uuid=chatroom_uuid, cookie=cookie)
    model_response = wrapper.summarize(query=message, embedding_model=embedding_model, chat_model=chat_model)
    think = re.findall(r"<think>.*<\/think>", model_response, re.DOTALL)
    return {"error": False, "data": {"think": think[0] if len(think) > 0 else None, "response": re.sub(r"<think>.*<\/think>", "", model_response, flags=re.DOTALL)}}

@router.get('/models')
async def get_models(request: Request, db: Session = Depends(get_db)):
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
async def update_models(request: Request, sessionToken: str, models: UpdateModelsParams, db: Session = Depends(get_db)):
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
async def update_models(request: Request, sessionToken: str, providers: UpdateProvidersParams, db: Session = Depends(get_db)):
    user = authentication_sdk.User(sessionToken, {})
    if not user.is_admin: return {"error": True, "status": "USER_NOT_AUTHORIZED"}
    db.execute(text('TRUNCATE TABLE providers'))

    for p in providers.providers:
        db.add(Provider(provider=p.provider, settings=p.settings))
    db.commit()

    return {"error": False, "status": "PROVIDERS_UPDATED"}

# May return sensitive info like API keys, so admin only
@router.get('/providers')
async def update_models(request: Request, sessionToken: str, db: Session = Depends(get_db)):
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
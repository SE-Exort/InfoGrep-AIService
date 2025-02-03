from fastapi import APIRouter, HTTPException, Request

from InfoGrep_BackendSDK import authentication_sdk, room_sdk
from Parsers.threadpool import ParserThreadPool
from Parsers import *

from LLMWrapers import Ollama, OpenAI

import requests

router = APIRouter(prefix='/api', tags=["api"]);
documentParserThreadPool = ParserThreadPool(10)

supportedFileTypes = dict();
for cls in Parser.Parser.__subclasses__():
    supportedFileTypes.update({cls.fileType(): cls})

@router.post('/start_parsing')
async def post_start_parsing(request: Request, chatroom_uuid, file_uuid, filetype, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers);

    parser: Parser;
    try:
        parser = supportedFileTypes[filetype](chatroom_uuid=chatroom_uuid, file_uuid=file_uuid, cookie=cookie)
    except:
        return 500

    documentParserThreadPool.submit_task(parser)
    return 200;

@router.post('/cancel_parsing')
def post_cancel_parsing(request: Request, chatroom_uuid, file_uuid, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers);

    taskkey = documentParserThreadPool.create_taskkey(chatroom_uuid=chatroom_uuid,file_uuid=file_uuid)

    documentParserThreadPool.cancel_task(taskkey=taskkey)
    
    return 200;

@router.get('/parsing_status')
def get_parsing_status(request: Request, chatroom_uuid, file_uuid, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers);
    
    taskkey = documentParserThreadPool.create_taskkey(chatroom_uuid=chatroom_uuid,file_uuid=file_uuid)
    documentParserThreadPool.get_task_status(taskkey=taskkey)
    return 200;

@router.get('/file_types')
async def get_file_types():
    return list(supportedFileTypes.keys())

"""For now we just have a weird setup to generate system messages.
In the future, we should take the chatroom uuid, the cookie, and the message uuid?????

Or should we just have a webhook and generate a response when needed instead of exposing an endpoint.
Either way, this service should send the message to the chatroom service."""
@router.get('/system_response')
async def get_system_Response(request: Request, chatroom_uuid, message, cookie, model):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, {})
    user_uuid = user.profile()['user_uuid']
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers)

    wrapper = None
    if model == "ollama":
        wrapper = Ollama.Ollama(chatroom_uuid=chatroom_uuid, cookie=cookie)
    else:
        wrapper = OpenAI.OpenAI(chatroom_uuid=chatroom_uuid, cookie=cookie)
    summarizedresponse = wrapper.summarize(message)

    r = room_sdk.post_message(chatroom_uuid=chatroom_uuid, message=summarizedresponse, cookie='infogrep-chatbot-summary', headers=request.headers, model=model)
    print(r.text)
    return summarizedresponse

@router.get('/models')
async def get_models(request: Request, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, request.headers)

    x = requests.get('http://localhost:11434/api/tags')
    model_list = x.json()['models']
    result = ["openai"]
    for model in model_list:
        print(f"Model Name: {model['name']}")
        result.append(model['name'])
    return result


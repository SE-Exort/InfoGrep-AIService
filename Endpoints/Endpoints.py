from fastapi import APIRouter, HTTPException

from InfoGrep_BackendSDK import authentication_sdk, room_sdk

from LLMWrapers import Ollama, OpenAI

import requests
router = APIRouter(prefix='/api', tags=["api"]);


"""For now we just have a weird setup to generate system messages.
In the future, we should take the chatroom uuid, the cookie, and the message uuid?????

Or should we just have a webhook and generate a response when needed instead of exposing an endpoint.
Either way, this service should send the message to the chatroom service."""
@router.get('/system_response')
async def get_system_Response(chatroom_uuid, message, cookie, model):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, {})
    user_uuid = user.profile()['user_uuid']
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers={})

    wrapper = None
    if model == "ollama":
        wrapper = Ollama.Ollama(chatroom_uuid=chatroom_uuid, cookie=cookie)
    else:
        wrapper = OpenAI.OpenAI(chatroom_uuid=chatroom_uuid, cookie=cookie)
    summarizedresponse = wrapper.summarize(message);

    r = room_sdk.post_message(chatroom_uuid=chatroom_uuid,message=summarizedresponse, cookie='infogrep-chatbot-summary', headers={}, model=model)
    print(r.text)
    return summarizedresponse

@router.get('/models')
async def get_models(cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, {})

    x = requests.get('http://localhost:11434/api/tags')
    model_list = x.json()['models']
    result = ["openai"]
    for model in model_list:
        print(f"Model Name: {model['name']}")
        result.append(model['name'])
    return result


from fastapi import APIRouter, HTTPException, Request

from InfoGrep_BackendSDK import authentication_sdk, room_sdk

from LLMWrapers import OpenAI

router = APIRouter(prefix='/api', tags=["api"]);


"""For now we just have a weird setup to generate system messages.
In the future, we should take the chatroom uuid, the cookie, and the message uuid?????

Or should we just have a webhook and generate a response when needed instead of exposing an endpoint.
Either way, this service should send the message to the chatroom service."""
@router.get('/system_response')
async def get_system_Response(request: Request, chatroom_uuid, message, cookie, openAIkey):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie, headers=request.headers)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie, headers=request.headers);

    a = OpenAI.OpenAI(chatroom_uuid=chatroom_uuid, cookie=cookie);
    a.set_openAIkey(openAIkey)
    summarizedresponse = a.summarize(message);

    room_sdk.post_message(chatroom_uuid=chatroom_uuid,message=summarizedresponse, cookie='infogrep-chatbot-summary', headers=request.headers)


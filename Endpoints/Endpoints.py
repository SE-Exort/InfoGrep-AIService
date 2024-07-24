from fastapi import APIRouter, HTTPException

from InfoGrep_BackendSDK import authentication_sdk, room_sdk

from LLMWrapers import Local

router = APIRouter(prefix='/api', tags=["api"]);


"""For now we just have a weird setup to generate system messages.
In the future, we should take the chatroom uuid, the cookie, and the message uuid?????

Or should we just have a webhook and generate a response when needed instead of exposing an endpoint.
Either way, this service should send the message to the chatroom service."""
@router.get('/system_response')
async def get_system_Response(chatroom_uuid, message, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie);

    a = Local.Local(chatroom_uuid=chatroom_uuid, cookie=cookie);
    summarizedresponse = a.summarize(message);

    room_sdk.post_message(chatroom_uuid=chatroom_uuid,message=summarizedresponse, cookie='infogrep-chatbot-summary')
    return summarizedresponse


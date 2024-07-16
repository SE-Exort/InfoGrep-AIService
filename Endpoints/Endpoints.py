from fastapi import APIRouter, HTTPException

from InfoGrep_BackendSDK import authentication_sdk, room_sdk

router = APIRouter(prefix='/api', tags=["api"]);

@router.post('/system_response')
async def get_system_Response(chatroom_uuid, message, cookie):
    #authenticate user
    #user must have a valid session cookie
    user = authentication_sdk.User(cookie)
    user_uuid = user.profile()['user_uuid'];
    room_sdk.get_userInRoom(chatroom_uuid=chatroom_uuid, cookie=cookie);


    return 200;

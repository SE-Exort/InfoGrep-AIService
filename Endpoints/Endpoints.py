from fastapi import APIRouter, Request

router = APIRouter(prefix='/api', tags=["api"]);

@router.post('/start_parsing')
async def post_start_parsing(request: Request, chatroom_uuid, file_uuid, filetype, cookie):
    return 200

@router.post('/cancel_parsing')
def post_cancel_parsing(request: Request, chatroom_uuid, file_uuid, cookie):
    return 200;

@router.get('/parsing_status')
def get_parsing_status(request: Request, chatroom_uuid, file_uuid, cookie):
    return 200;

@router.get('/file_types')
async def get_file_types():
    return 200

"""For now we just have a weird setup to generate system messages.
In the future, we should take the chatroom uuid, the cookie, and the message uuid?????

Or should we just have a webhook and generate a response when needed instead of exposing an endpoint.
Either way, this service should send the message to the chatroom service."""
@router.get('/system_response')
async def get_system_Response(request: Request, chatroom_uuid, message, cookie, model):
    return 200

@router.get('/models')
async def get_models(request: Request, cookie):
    return 200

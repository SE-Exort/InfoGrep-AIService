import os

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from Endpoints.Endpoints import router
AIService = FastAPI();

os.environ["no_proxy"]="*"
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
origins = [
    "*",
]

@AIService.middleware("http")
async def add_open_telemetry_headers(request: Request, call_next):
    response = await call_next(request)
    for k, v in request.headers.items():
        if k.startswith("x-") or k.startswith("trace"):
            response.headers[k] = v
    return response

AIService.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AIService.include_router(router)

if __name__ == "__main__":
    uvicorn.run(AIService, host="0.0.0.0", port=8004)
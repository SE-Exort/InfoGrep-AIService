import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from Endpoints.Endpoints import router
from InfoGrep_BackendSDK.service_endpoints import ollama_service_host
from InfoGrep_BackendSDK.middleware import TracingMiddleware, LoggingMiddleware
from InfoGrep_BackendSDK.infogrep_logger.logger import Logger

AIService = FastAPI()
ai_service_logger = Logger("AIServiceLogger")

os.environ["no_proxy"]="*"
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
origins = [
    "*",
]

AIService.add_middleware(LoggingMiddleware, logger=ai_service_logger)
AIService.add_middleware(TracingMiddleware)
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
import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import requests

from Endpoints.Endpoints import router
from Endpoints.utils import download_model
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

DefaultModels = ["deepseek-r1"]
if __name__ == "__main__":
    # ensure Ollama is running and has default models
    for model in DefaultModels:
        download_model("ollama", model)
    
    # ensure milvus is running
    requests.get(f'http://localhost:19530/v1/vector/collections', headers={'Accept': 'application/json'})
    uvicorn.run(AIService, host="0.0.0.0", port=8004)
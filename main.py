from fastapi import FastAPI;
import uvicorn
from Endpoints.Endpoints import router
import requests
AIService = FastAPI()

AIService.include_router(router)

DefaultModels = ["deepseek-r1"]
if __name__ == "__main__":
    # ensure Ollama is running and has default models
    for model in DefaultModels:
        r = requests.post('http://localhost:11434/api/pull', json={'model': model})
        print(r.text)
    uvicorn.run(AIService, host="0.0.0.0", port=8004)
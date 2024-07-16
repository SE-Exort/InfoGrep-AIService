from fastapi import FastAPI;
import uvicorn
from Endpoints.Endpoints import router
AIService = FastAPI();

AIService.include_router(router)
if __name__ == "__main__":
    uvicorn.run(AIService, host="0.0.0.0", port=8004)
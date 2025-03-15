import re
import requests
from InfoGrep_BackendSDK.service_endpoints import ollama_service_host

def download_model(provider: str, model: str):
    if not (provider == "ollama"): return
    print("Downloading model provider {provider}, model {model}")
    requests.post(f'http://{ollama_service_host}/api/pull', json={'model': model})

# Milvus is picky about collection name, so convert model names into an acceptable stripped form
def convert_collection_name(model_name: str):
    return re.sub('[^0-9a-zA-Z]+', '_', model_name)
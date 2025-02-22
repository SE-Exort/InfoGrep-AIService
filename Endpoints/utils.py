import requests
from InfoGrep_BackendSDK.service_endpoints import ollama_service_host

def download_model(provider: str, model: str):
    if not (provider == "ollama"): return
    print("Downloading model provider {provider}, model {model}")
    requests.post(f'http://{ollama_service_host}/api/pull', json={'model': model})
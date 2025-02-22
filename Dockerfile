FROM python:3.10.14

COPY . /app
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

RUN --mount=type=cache,target=/root/.cache \
    pip install -r ./InfoGrep_BackendSDK/requirements.txt

EXPOSE 8004
CMD ["python3", "main.py"]


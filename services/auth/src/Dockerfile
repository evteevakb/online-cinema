FROM python:3.13.2-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY requirements.txt requirements.txt

RUN apt-get update \
 && apt-get install --no-install-recommends -y curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd -r auth \
 && useradd -r -g auth auth \ 
 && chown -R auth:auth /src \
 && pip3 install --no-cache-dir --upgrade pip \
 && pip3 install --no-cache-dir -r requirements.txt

COPY . .

USER auth

CMD ["sh", "-c", "gunicorn main:app --bind $API_HOST:$API_PORT -k uvicorn.workers.UvicornWorker"]

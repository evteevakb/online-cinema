FROM python:3.11.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
 && apt-get install --no-install-recommends -y curl=7.88.1-10+deb12u12 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd -r flask \
 && useradd -r -g flask flask \ 
 && chown -R flask:flask /app \
 && pip3 install --no-cache-dir --upgrade pip==23.2.1 \
 && pip3 install --no-cache-dir --requirement requirements.txt

COPY . .

USER flask

CMD ["sh", "-c", "gunicorn -b ${API_HOST}:${API_PORT} app:app"]

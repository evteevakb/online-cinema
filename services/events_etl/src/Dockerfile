FROM python:3.11.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /etl

COPY requirements.txt .

RUN groupadd -r etl \
 && useradd -r -g etl etl \ 
 && chown -R etl:etl /etl \
 && pip3 install --no-cache-dir --upgrade pip==23.2.1 \
 && pip3 install --no-cache-dir --requirement requirements.txt

COPY . .

USER etl

CMD ["python", "main.py"]

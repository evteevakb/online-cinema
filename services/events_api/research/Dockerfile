FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY requirements.txt requirements.txt

RUN apt-get update \
 && apt-get install --no-install-recommends -y curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd -r research \
 && useradd -r -g research research \
 && chown -R research:research /src \
 && pip3 install --no-cache-dir --upgrade pip \
 && pip3 install --no-cache-dir -r requirements.txt

COPY . .

USER research

CMD ["python", "-m", "main"]
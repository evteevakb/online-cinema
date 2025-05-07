FROM python:3.13.2-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /tests

COPY pytest.ini requirements.txt ./

RUN groupadd -r tests \
 && useradd -r -g tests tests \ 
 && chown -R tests:tests /tests \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --requirement requirements.txt

USER tests

COPY . .

ENTRYPOINT ["sh", "-c", "python3 -m utils.wait_for_es \
                      && python3 -m utils.wait_for_redis \
                      && python3 -m utils.wait_for_api \
                      && python3 -m pytest ."]

FROM python:3.13.1

ENV DJANGO_SETTINGS_MODULE='config.settings'
# prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN groupadd -r django \
 && useradd -r -g django django \ 
 && mkdir -p /app/staticfiles \
 && chown -R django:django /app/staticfiles \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

USER django

COPY . .

ENTRYPOINT ["/app/run_uwsgi.sh"]

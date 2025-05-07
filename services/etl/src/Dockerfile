FROM python:3.13.1

# prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /etl

COPY requirements.txt requirements.txt

RUN groupadd -r etl \
 && useradd -r -g etl etl \
 && chown -R etl:etl /etl \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

USER etl

COPY . .

CMD ["python", "etl_process.py"]
# CMD ["python", "etl_load_genres.py"]
# CMD ["python", "etl_load_persons.py"]
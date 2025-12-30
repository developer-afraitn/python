FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    locales-all \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=fa_IR.UTF-8
ENV LANGUAGE=fa_IR:fa
ENV LC_ALL=fa_IR.UTF-8

COPY requirements.txt .
#RUN pip install --no-cache-dir -U pip setuptools wheel \ && pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]

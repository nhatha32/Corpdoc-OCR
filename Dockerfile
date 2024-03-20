FROM python:3.10-slim

WORKDIR /app

COPY . /app

ENV PYHTONUNBUFFERED=1

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && apt-get -y install tesseract-ocr-vie

RUN apt-get install poppler-utils -y

RUN pip install -r requirements.txt

CMD uvicorn src.main:app --reload --port=9000 --host=0.0.0.0
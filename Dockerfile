FROM python:3.10-slim

WORKDIR /app

COPY . /app

ENV PYHTONUNBUFFERED=1

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && apt-get -y install tesseract-ocr-vie

RUN pip install -r requirements.txt

CMD uvicorn main:app --reload --port=8080 --host=0.0.0.0
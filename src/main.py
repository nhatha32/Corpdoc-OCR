from fastapi import FastAPI
from src.OCR import OCRProcessor
from src.rabbitMQ import consumer_channel
from src.envLoader import amqp_ocr_queue
import threading

# Initialize FastAPI
app = FastAPI()


# Define FastAPI route
@app.get("/")
def index():
    return {"vi": "Dịch vụ OCR đang chạy...", "en": "OCR service is running..."}


# Start the RabbitMQ consumer
def start_consumer():
    consumer_channel.queue_declare(queue=amqp_ocr_queue, durable=True)

    def callback(ch, method, properties, body):
        data = body.decode("utf-8")
        ids = data.split("|")
        OCRProcessor(ids[0], ids[1], ids[2])

    consumer_channel.basic_consume(amqp_ocr_queue, callback, auto_ack=True)
    consumer_channel.start_consuming()


if __name__ == "src.main":
    # Start the consumer in a separate thread
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.start()

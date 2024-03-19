#######################   FUNCTION   #############################

from OCR import OCRProcessor
from rabbitMQ import consumer_channel

##################################################################
##################################################################

#######################   VARIABLE   #############################

from envLoader import amqp_ocr_queue

##################################################################
##################################################################

consumer_channel.queue_declare(queue=amqp_ocr_queue, durable=True)


def callback(ch, method, properties, body):
    id = body.decode("utf-8")
    OCRProcessor(id)


consumer_channel.basic_consume(amqp_ocr_queue, callback, auto_ack=True)
consumer_channel.start_consuming()

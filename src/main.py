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
    data = body.decode("utf-8")
    ids = data.split("|")
    OCRProcessor(ids[0], ids[1])


consumer_channel.basic_consume(amqp_ocr_queue, callback, auto_ack=True)
consumer_channel.start_consuming()

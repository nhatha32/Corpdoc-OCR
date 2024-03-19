###################### LIBRARY ###################################

import pika

##################################################################
##################################################################

#######################   VARIABLE   #############################

from envLoader import (
    amqp_protocol,
    amqp_username,
    amqp_password,
    amqp_hostname,
    amqp_vhost,
)

##################################################################
##################################################################

amqp_url = (
    f"{amqp_protocol}://{amqp_username}:{amqp_password}@{amqp_hostname}/{amqp_vhost}"
)
params = pika.URLParameters(amqp_url)

# Producer connection
producer_conn = pika.BlockingConnection(params)
producer_channel = producer_conn.channel()

# Consumer connection
consumer_conn = pika.BlockingConnection(params)
consumer_channel = consumer_conn.channel()

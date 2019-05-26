#!/usr/bin/env python
import pika
import time
import random

# start a connection with localhost
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('172.17.9.74', 5672, '/', credentials))
channel = connection.channel()

# this is a queue named hello
channel.queue_declare('decibel_three')


while True:
    #sending hello world with routing key which refers to queue
    i = random.randint(1, 101)
    channel.basic_publish(exchange='',
                          routing_key='decibel_three',
                          body=str(i))
    print("dB sent: ", str(i))
    time.sleep(1)

# close connection
connection.close()
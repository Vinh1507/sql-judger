import pika
import time
import random

import pika.exchange_type
# import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import json
import sql_judge

def on_message_received(ch, method, properties, body):
    
    data = json.loads(body.decode('utf-8'))
    print(data)
    executor.submit(sql_judge.judge_submission, data)

exchange_name = 'topic_sql_judge'
queue_name = 'mysql_letterbox'
pattern = "mysql.#"

def start_consumer():
    connection_parameters = pika.ConnectionParameters('localhost')
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
    queue = channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=3)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=pattern)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message_received, auto_ack=True)
    print("Starting Competing Consuming")
    channel.start_consuming()

executor = ThreadPoolExecutor(max_workers=3)
start_consumer()
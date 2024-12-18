import pika
import pika.exchange_type
from concurrent.futures import ThreadPoolExecutor
import json
from judger import sql_judge
from dotenv import load_dotenv
import os
import time

load_dotenv()

def on_message_received(ch, method, properties, body):
    try:
        data = json.loads(body.decode('utf-8'))
        print("RECEIVED MESSAGE")
        sql_judge.judge_submission(data, ch, method)
        
    except Exception as e:
        print(e)

port = os.getenv('RABBITMQ_PORT', 5672) 
host = os.getenv('RABBITMQ_HOST')
exchange_name = os.getenv('RABBITMQ_EXCHANGE_NAME')
queue_name = os.getenv('RABBITMQ_QUEUE_NAME')
pattern = os.getenv('JUDGER_PATTERN')

def start_consumer():
    max_retries = 50000000  # Số lần retry tối đa
    retry_count = 0  # Đếm số lần retry
    
    while retry_count < max_retries:
        try:
            # Thiết lập kết nối
            connection_parameters = pika.ConnectionParameters(host, port)
            connection = pika.BlockingConnection(connection_parameters)
            channel = connection.channel()

            # Cấu hình exchange và queue
            channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
            queue = channel.queue_declare(queue=queue_name)
            channel.basic_qos(prefetch_count=3)
            channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=pattern)

            # Bắt đầu tiêu thụ tin nhắn
            channel.basic_consume(queue=queue_name, on_message_callback=on_message_received, auto_ack=False)
            print("Start Consuming")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            retry_count += 1
            print(f"Connection error: {e}. Retrying {retry_count}/{max_retries} in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            retry_count += 1
            print(f"Unexpected error: {e}. Retrying {retry_count}/{max_retries} in 5 seconds...")
            time.sleep(5)
        else:
            # Nếu kết nối thành công, reset retry_count về 0
            retry_count = 0
    
    print("Exceeded maximum retry attempts. Exiting...")

start_consumer()
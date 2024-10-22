import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import requests
# from tabulate import tabulate
from broker import rabbitmq_broker
import os
# from dotenv import load_dotenv
import requests
import json
import subprocess
import redis
from datetime import datetime
import resource

import time
import mysql_judge

client = redis.Redis(host='localhost', port=6380, db=0)

# Hàm giới hạn tài nguyên cho tiến trình
def limit_resources(memory_limit_MB):
    # Giới hạn bộ nhớ tối đa cho tiến trình (trong KB)
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit_MB, memory_limit_MB))

def test_func(timeout):
    time.sleep(timeout)

@dramatiq.actor
def judge_one_testcase(issue, testcase):
    memory_limit = issue['memory_limit'] # MB
    limit_resources(memory_limit * 1024 * 1024)

    print(f"Tiến trình Testcase {os.getpid()} bắt đầu")
    mysql_judge.judge_one_testcase(issue, testcase)
    print(f"Tiến trình Testcase {os.getpid()} hoàn thành.")

    # try:
    #     print(f"Tiến trình {os.getpid()} bắt đầu với lệnh: {command}")
    #     # Chạy lệnh với timeout
    #     process = subprocess.Popen(command, shell=True)
    #     process.wait(timeout=time_limit)
    #     print(f"Tiến trình {os.getpid()} hoàn thành.")
    # except subprocess.TimeoutExpired:
    #     print(f"Tiến trình {os.getpid()} đã vượt quá thời gian cho phép, tiến hành dừng...")
    #     process.terminate()
    #     process.wait()  # Đợi tiến trình dừng
    #     return 124  # Mã lỗi cho timeout
    # return process.returncode
    



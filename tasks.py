import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import requests
from broker import rabbitmq_broker
import os
import requests
import json
import subprocess
import redis
from datetime import datetime
import resource
import time
import mysql_judge
from judger_exception import JudgerException

client = redis.Redis(host='localhost', port=6380, db=0)

def limit_resources(memory_limit_MB):
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit_MB, memory_limit_MB))

def test_func(timeout):
    time.sleep(timeout)

@dramatiq.actor
def judge_one_testcase(result_queue, issue, testcase):
    memory_limit = issue['memory_limit']  # MB
    limit_resources(memory_limit * 1024 * 1024)

    print(f"Process Testcase {os.getpid()} started.")
    
    try:
        mysql_judge.judge_one_testcase(issue, testcase)
    except JudgerException as e:
        result_queue.put((e.status))
    
    print(f"Process Testcase {os.getpid()} finished.")
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import requests
import os
import requests
import json
import subprocess
import redis
from datetime import datetime
import resource
import time
import judger.mysql_judge as mysql_judge
from exceptions.judger_exception import JudgerException
from judger import sql_server_judge
from constants.submission_constants import LanguageConstant

def limit_resources(memory_limit_MB):
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit_MB, memory_limit_MB))

def judge_one_test_case(result_queue, data, test_case_index):
    question = data['question']
    memory_limit = question['memory_limit']  # MB
    limit_resources(memory_limit * 1024 * 1024)
    # limit_resources(3000 * 1024 * 1024)

    print(f"Process Testcase {os.getpid()} started.")
    language = data['language']
    try:
        if language == LanguageConstant.MYSQL_INDEX:
            mysql_judge.judge_one_test_case(data, test_case_index)
        elif language == LanguageConstant.SQL_SERVER_INDEX:
            sql_server_judge.judge_one_test_case(data, test_case_index)
    except JudgerException as e:
        result_queue.put(e.get_data())
    
    print(f"Process Testcase {os.getpid()} finished.")
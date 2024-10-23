import multiprocessing
import subprocess
import os
import time
import tasks
from dotenv import load_dotenv
import requests

load_dotenv()


# testcase1 = {
#     'input_judge_sql': """
#     CREATE TABLE test_table (
#         id INT,
#         name VARCHAR(50)
#     );
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob');
#     """,
# }
# testcase2 = {
#     'input_judge_sql': """
#     CREATE TABLE test_table (
#         id INT,
#         name VARCHAR(50)
#     );
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob \n Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#     """,
# }

# issue = {
#     'time_limit': 0.2,
#     'memory_limit': 180,
#     'testcases': [testcase1, testcase2],
#     'check_judge_sql': """
#     SELECT * FROM test_table;
#     """
# }

def judge_submission(data):
    user = data['user']
    issue = data['issue']
    submission = data['submission']
    type = data['type']

    processes = []
    result_queue = multiprocessing.Queue()

    for testcase in issue['testcases']:
        # tasks.judge_one_testcase.send(result_queue, data, testcase)
        p = multiprocessing.Process(target=tasks.judge_one_testcase, args=(result_queue, data, testcase))
        processes.append(p)
        p.start()      
    
    for p in processes:
        p.join()

    final_status, accepted_counter, first_error_status, max_execution_time = None, 0, None, 0
    while not result_queue.empty():
        result_testcase = result_queue.get()
        max_execution_time = max(max_execution_time, result_testcase['execution_time'])
        if result_testcase['status'] == 'AC':
            accepted_counter += 1
        elif first_error_status is None:
            first_error_status = result_testcase['status']
    
    if accepted_counter == len(issue['testcases']) and first_error_status is None:
        final_status = 'AC'
    else:
        final_status = first_error_status
    
    print("All processes have completed or been stopped.")

    update_submission_data = {
        'submission': {
            "id": submission['id'],
            "status": final_status,
            'execution_time': max_execution_time,
        }
    }
    try:
        response = requests.post(f"{os.getenv('SQL_LAB_SERVER_URL') + '/judge/update-submission-status'}", json=update_submission_data)
        if response.status_code == 201:
            # In nội dung phản hồi
            print("Response data:", response.json())
        else:
            print(f"Request failed with status code: {response.status_code}")

    except Exception as e:
        pass


# judge_submission({
#     'user': {
#         'username': 'vinhbh'
#     },
#     'issue': issue,
#     'submission': {
#         'user_sql': """
#         INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
#         """,
#     },
# })
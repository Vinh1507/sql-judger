import multiprocessing
import subprocess
import os
import time
import tasks
from dotenv import load_dotenv
import requests
from constants import SubmissionStatus

load_dotenv()

def judge_submission(data:dict):
    try:
        user = data['user']
        issue = data['issue']
        submission:dict = data['submission']
        target_type = data.get('type', SubmissionStatus.TYPE_JUDGE_SUBMISSION)

        processes = []
        result_queue = multiprocessing.Queue()

        for testcase_index in range(len(issue['testcases'])):
            p = multiprocessing.Process(target=tasks.judge_one_testcase, args=(result_queue, data, testcase_index))
            processes.append(p)
            p.start()      
        
        for p in processes:
            p.join()

        final_status, accepted_testcase_count, first_error_status, max_execution_time, first_message, outputs = None, 0, None, 0, '', []
        while not result_queue.empty():
            result_testcase = result_queue.get()
            print(result_testcase)
            print(1)
            max_execution_time = max(max_execution_time, result_testcase['execution_time'])
            print(2)
            if result_testcase['status'] == SubmissionStatus.ACCEPTED:
                accepted_testcase_count += 1
                # outputs.append(result_testcase['output'])
            elif first_error_status is None:
                print(3)    
                first_error_status = result_testcase['status']
                first_message = result_testcase['message']
                # outputs.append(None)
        
        if accepted_testcase_count == len(issue['testcases']) and first_error_status is None:
            final_status = SubmissionStatus.ACCEPTED
        else:
            final_status = first_error_status
        
        print("All processes have completed or been stopped.")

        if target_type == SubmissionStatus.TYPE_JUDGE_SUBMISSION:
            update_submission_data = {
                'submission': {
                    "id": submission.get('id', None),
                    "status": final_status,
                    'execution_time': max_execution_time,
                    # 'outputs': 
                }
            }

            print(update_submission_data)
            response = requests.post(f"{os.getenv('SQL_LAB_SERVER_URL') + '/judge/update-submission-status'}", json=update_submission_data)
        elif target_type == SubmissionStatus.TYPE_VALIDATE_CREATE_ISSUE:
            issue__validation_data = {
                'validateResult': {
                    'isSuccess': final_status == SubmissionStatus.VALID,
                    'issue': {
                        'code': issue['code'],
                    },
                    'message': first_message,
                    # 'outputs': outputs
                },
                'isUpdateExistedIssue': data.get('update_existed_issue', False)
            }
            response = requests.post(f"{os.getenv('SQL_LAB_SERVER_URL') + '/judge/update-issue-status'}", json=issue__validation_data)
            
    except Exception as e:
        print(e)
        pass

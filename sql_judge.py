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
        question = data['question']
        submission:dict = data['submission']
        target_type = data.get('type', SubmissionStatus.TYPE_JUDGE_SUBMISSION)

        processes = []
        result_queue = multiprocessing.Queue()

        for testcase_index in range(len(question['test_cases'])):
            p = multiprocessing.Process(target=tasks.judge_one_testcase, args=(result_queue, data, testcase_index))
            processes.append(p)
            p.start()      
        
        for p in processes:
            p.join()

        final_status, accepted_testcase_count, first_error_status, max_execution_time, first_message = None, 0, None, 0, ''
        user_outputs = []
        testcase_judgement_audit = []
        while not result_queue.empty():
            result_testcase = result_queue.get()
            max_execution_time = max(max_execution_time, result_testcase['execution_time'])
            testcase_judgement_audit.append({
                **result_testcase,
            })
            user_outputs.append({
                "testCase": {
                    'index': result_testcase.get('test_case_index'),
                    'id': result_testcase.get('test_case_id'),
                },
                "text": result_testcase.get('user_output')
            })

            if result_testcase['status'] == SubmissionStatus.ACCEPTED:
                accepted_testcase_count += 1
                
            elif first_error_status is None: 
                first_error_status = result_testcase['status']
                first_message = result_testcase['message']
            
        
        if accepted_testcase_count == len(question['test_cases']) and first_error_status is None:
            final_status = SubmissionStatus.ACCEPTED
        else:
            final_status = first_error_status
        
        print("All processes have completed or been stopped.", testcase_judgement_audit)

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
        elif target_type == SubmissionStatus.TYPE_VALIDATE_CREATE_QUESTION:
            question__validation_data = {
                'validateResult': {
                    'isSuccess': final_status == SubmissionStatus.VALID,
                    'question': {
                        'code': question['code'],
                    },
                    'message': first_message,
                    'outputs': user_outputs
                },
                'isUpdateExistedQuestion': data.get('update_existed_question', False)
            }
            response = requests.post(f"{os.getenv('SQL_LAB_SERVER_URL') + '/judge/update-question-status'}", json=question__validation_data)
            
    except Exception as e:
        print(e)
        pass

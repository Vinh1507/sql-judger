import multiprocessing
import subprocess
import os
import time
import judger.tasks as tasks
from dotenv import load_dotenv
import requests
from constants.submission_constants import SubmissionStatus
import helpers.storage_helper as storage_helper
from api import api_helper
load_dotenv()

def judge_submission(data:dict):
    try:
        user = data['user']
        submission:dict = data['submission']
        target_type = data.get('type', SubmissionStatus.TYPE_JUDGE_SUBMISSION)
        language = data['language']
        question:dict = data['question']
        saved_data:dict = data.get('saved_data', {})
        input_test_cases_from_s3 = storage_helper.read_input_zip_file(storage_helper.default_bucket_name, question.get('input_file_path'))
        question['test_cases'] = []

        for input_test_case in input_test_cases_from_s3:
            question['test_cases'].append({
                'input': {
                    'file_name': input_test_case.get('file_name'),
                    'text': input_test_case.get('text')
                }
            })

        if target_type == SubmissionStatus.TYPE_JUDGE_SUBMISSION:
            output_test_cases_from_s3 = storage_helper.read_output_zip_file(storage_helper.default_bucket_name, question.get('output_file_path'))
            if(len(output_test_cases_from_s3) != len(input_test_cases_from_s3)):
                # TODO: Throw exception
                pass

            for output_test_case_index in range(len(output_test_cases_from_s3)):
                output_test_case = output_test_cases_from_s3[output_test_case_index]
                question['test_cases'][output_test_case_index]['output'] = {
                    'file_name': output_test_case.get('file_name'),
                    'text': output_test_case.get('text')
                }

        print(question['test_cases'])
        processes = []
        result_queue = multiprocessing.Queue()

        # Use Multi processes to evaluate submission. Each test case has been run in a single process
        for test_case_index in range(len(question['test_cases'])):
            p = multiprocessing.Process(target=tasks.judge_one_test_case, args=(result_queue, data, test_case_index))
            processes.append(p)
            p.start()      
        
        for p in processes:
            p.join()

        final_status = None
        accepted_test_case_count, first_error_status, max_execution_time, first_message = 0, None, 0, ''
        user_outputs = []
        test_case_judgement_audit = []
        while not result_queue.empty():
            result_test_case = result_queue.get()
            max_execution_time = max(max_execution_time, result_test_case['execution_time'])
            test_case_judgement_audit.append({
                **result_test_case,
            })
            user_outputs.append({
                "test_case": {
                    'index': result_test_case.get('test_case_index'),
                    'id': result_test_case.get('test_case_id'),
                    'input_file_name': result_test_case.get('input_file_name'),
                    "output_text": result_test_case.get('user_output')
                },
            })

            if result_test_case['status'] == SubmissionStatus.ACCEPTED:
                accepted_test_case_count += 1
                
            elif first_error_status is None: 
                first_error_status = result_test_case['status']
                first_message = result_test_case['message']
            
        
        if accepted_test_case_count == len(question['test_cases']) and first_error_status is None:
            final_status = SubmissionStatus.ACCEPTED
        else:
            final_status = first_error_status
        
        print("All processes have completed or been stopped.", test_case_judgement_audit)

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
            apiHelper = api_helper.ApiHelper()
            response = apiHelper.post(endpoint='/judge/update-submission-status', json_data=update_submission_data)

        elif target_type == SubmissionStatus.TYPE_VALIDATE_CREATE_QUESTION:
            user_outputs = sorted(user_outputs, key=lambda x: x['test_case']['index'])
            if(data.get('save_standard_input_output', False)): 
                storage_helper.upload_input_zip_file(storage_helper.default_bucket_name, saved_data.get('input_file_path'), question['test_cases'])
                storage_helper.upload_output_zip_file(storage_helper.default_bucket_name, saved_data.get('output_file_path'), user_outputs)
            question_validation_data = {
                'validateResult': {
                    'isSuccess': final_status == SubmissionStatus.VALID,
                    'languageName': language,
                    'question': {
                        'code': question['code'],
                    },
                    'message': first_message,
                    'outputs': user_outputs,
                    'executionTime': max_execution_time,
                },
                'requestId': data.get('request_id'),
                'savedData': {
                    'inputFilePath': saved_data.get('input_file_path', None),
                    'outputFilePath': saved_data.get('output_file_path', None),
                    'additionalCheckCode': question.get('additional_check_code', None),
                    'standardSolutionCode': submission.get('user_sql', None),
                    'exampleTestCases': question.get('example_test_cases', 0),
                },
                'isSaveQuestionLanguage': data.get('save_question_language', False)
            }

            apiHelper = api_helper.ApiHelper()
            response = apiHelper.post(endpoint='/judge/update-question-status', json_data=question_validation_data)
    except Exception as e:
        e.with_traceback
        print(e)
        pass

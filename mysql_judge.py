import db_connection
import uuid
import time
from dotenv import load_dotenv
import mysql.connector
import subprocess
from datetime import datetime
import json
import os
import file_helper
from judger_exception import JudgerException
from constants import SubmissionStatus
import storage_helper
import redis
from minio import Minio
from minio.error import S3Error

load_dotenv()

redis_client = redis.StrictRedis(host='localhost', port=6380, db=0)

def create_isolated_database(test_case_data, db_name):
    try:
        sql_commands = f"""
        CREATE DATABASE {db_name};
        GRANT CREATE, ALTER, INSERT, DROP, UPDATE, DELETE, SELECT, REFERENCES ON {db_name}.* TO '{os.getenv('DB_S2_USERNAME')}'@'%';
        FLUSH PRIVILEGES;
        """
        s1_connection, s1_cursor = db_connection.get_s1_connection_and_cursor()
        for command in sql_commands.split(';'):
            if command.strip():
                s1_cursor.execute(command)

        s1_connection.commit()
    except Exception as e:
        print(e)
        raise JudgerException(
            **test_case_data,
            status=SubmissionStatus.INTERNAL_ERROR,
        )
    
def execute_input_code(test_case_data, sql_file_name, sql_code):
    try:
        file_helper.create_file(sql_file_name, sql_code)
        command = f"mysql -h {os.getenv('DB_BASE_HOST')} -P {os.getenv('DB_BASE_PORT')} -p{os.getenv('DB_S2_PASSWORD')} -u {os.getenv('DB_S2_USERNAME')} < {sql_file_name}"
        
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
        )
        return {
            'output': result.stdout,
        }

    except subprocess.CalledProcessError as e:
        raise JudgerException(
            **test_case_data,
            status=SubmissionStatus.RUNTIME_ERROR,
            message=e.stderr,
        )
    except Exception as e:
        raise JudgerException(
            **test_case_data,
            status=SubmissionStatus.RUNTIME_ERROR,
        )
        
def execute_solution(test_case_data, sql_file_name, sql_code, time_limit):
    try:
        start_time = time.time()
        file_helper.create_file(sql_file_name, sql_code)
        command = f"mysql -h {os.getenv('DB_BASE_HOST')} -P {os.getenv('DB_BASE_PORT')} -p{os.getenv('DB_S2_PASSWORD')} -u {os.getenv('DB_S2_USERNAME')} < {sql_file_name}"
        
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            timeout=time_limit
        )
        end_time = time.time()
        execution_time = end_time - start_time
        # print(result.stdout)
        return {
            'user_output': result.stdout,
            'execution_time': execution_time
        }
    except subprocess.TimeoutExpired as e:
        raise JudgerException(
            **test_case_data,
            status=SubmissionStatus.TIME_LIMIT_EXCEEDED,
            message=e.stderr,
            execution_time=time_limit
        )
    except subprocess.CalledProcessError as e:
        raise JudgerException(
            **test_case_data,
            status=SubmissionStatus.RUNTIME_ERROR,
            message=e.stderr,
        )
    except Exception as e:
        raise JudgerException(
            **test_case_data,
            status=SubmissionStatus.RUNTIME_ERROR,
        )

# def get_expected_output(test_case_data, object_name):
#     """
#     Redis cache in 24 hours
#     """
#     data_from_redis = redis_client.get(object_name)
    
#     if data_from_redis is not None:
#         print(f"Dữ liệu đã được lấy từ Redis với object_name '{object_name}'.")
#         return data_from_redis.decode('utf-8')  # Giả sử dữ liệu là chuỗi

#     # Nếu không có dữ liệu trong Redis, lấy từ MinIO
#     try:
#         # Lấy đối tượng từ MinIO
#         data_from_storage = storage_helper.read_file(bucket_name=storage_helper.default_bucket_name, object_name=object_name)
        
#         # Lưu dữ liệu vào Redis để sử dụng sau này
#         redis_client.set(object_name, data_from_storage, ex=86400)
#         print(f"Dữ liệu đã được lấy từ MinIO và lưu vào Redis với object_name '{object_name}'.")
        
#         return data_from_storage
#     except S3Error as exc:
#         print(f"Lỗi khi lấy dữ liệu từ MinIO: {exc}")
#         raise JudgerException (
#             **test_case_data,
#             status=SubmissionStatus.INTERNAL_ERROR
#         )
        

def compare_output(test_case_data, user_output: str, expected_output: str) -> str:
    compare_status = SubmissionStatus.WRONG_ANSWER
    try:
        # expected_output = file_helper.read_file(expected_output_file_path)
        if user_output.strip() == expected_output.strip():
            compare_status = SubmissionStatus.ACCEPTED
        return compare_status
    except:
        raise JudgerException(
            **test_case_data,
            status=SubmissionStatus.INTERNAL_ERROR,
        )

# def save_standard_output(standard_output_text, question_postfix: str, language: str, test_case_index):
#     object_name = f"output_question-{question_postfix}_lang-{language}_tc{test_case_index}.txt"
#     storage_helper.upload_file_from_content(storage_helper.default_bucket_name, object_name, standard_output_text)

def remove_isolated_database(db_name):
    try:
        sql_commands = f"""
        REVOKE ALL PRIVILEGES ON {db_name}.* FROM '{os.getenv('DB_S2_USERNAME')}'@'%';
        DROP DATABASE {db_name};
        """
        s1_connection, s1_cursor = db_connection.get_s1_connection_and_cursor()
        for command in sql_commands.split(';'):
            if command.strip():
                s1_cursor.execute(command)

        s1_connection.commit()
    except:
        pass


def judge_one_test_case(question: dict, data: dict, test_case_index: int) -> None:
    try:
        user = data['user']
        question = data['question']
        # print(question['test_cases'])
        submission = data['submission']
        target_type = data.get('type', SubmissionStatus.TYPE_JUDGE_SUBMISSION)
        need_compare_result = target_type == SubmissionStatus.TYPE_JUDGE_SUBMISSION
        test_case = question['test_cases'][test_case_index]
        test_case_data = {
            'question_id': question.get('id', None),
            'lang': 'mysql',
            'test_case_id': test_case.get('id', None),
            'test_case_index': test_case_index,
            'input_file_name': test_case['input']['file_name'],
            'submission_id': submission.get('id', None),
        }

        uuid4 = uuid.uuid4()
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        db_name = user['username'] + current_time + '_' + str(uuid4)[:10].replace('-', '_')

        create_isolated_database(test_case_data, db_name)

        input_code = f"""
        USE {db_name};
        {test_case['input']['text']}
        """
        input_file_name = db_name + '_input' + '.sql'
        execute_input_code(test_case_data, os.path.join(os.getenv('SOLUTION_DIR'), input_file_name), input_code)

        solution_code = f"""
        USE {db_name};
        {submission['user_sql']}
        {question['additional_check_code']}
        """

        solution_file_name = db_name + '.sql'
        execution_result = execute_solution(test_case_data, os.path.join(os.getenv('SOLUTION_DIR'), solution_file_name), solution_code, question['time_limit'])
        # print(f"Thời gian thực thi truy vấn: {execution_result['execution_time']:.6f} giây")
        if need_compare_result:
            expected_output = test_case['output']['text']
            compare_status = compare_output(test_case_data, execution_result['user_output'], expected_output)
            raise JudgerException(
                **test_case_data,
                status=compare_status,
                execution_time=execution_result['execution_time'],
                user_output=execution_result['user_output'],
                expected_output=expected_output,
            )
        else:
            print(type(execution_result['execution_time']))
            raise JudgerException(
                **test_case_data,
                status=SubmissionStatus.VALID,
                execution_time=execution_result['execution_time'],
                user_output=execution_result['user_output'],
            )

            
    except JudgerException as e:
        print("STATUS", e.status, e.execution_time)
        raise e
    except Exception as e:
        print(e)
    finally:
        try:
            remove_isolated_database(db_name)
            file_helper.delete_file(os.path.join(os.getenv('SOLUTION_DIR'), input_file_name))
            file_helper.delete_file(os.path.join(os.getenv('SOLUTION_DIR'), solution_file_name))
        except:
            pass
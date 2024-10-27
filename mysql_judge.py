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

def create_isolated_database(testcase_data, db_name):
    try:
        sql_commands = f"""
        CREATE DATABASE {db_name};
        GRANT CREATE, ALTER, INSERT, DROP, UPDATE, DELETE, SELECT ON {db_name}.* TO '{os.getenv('DB_S2_USERNAME')}'@'%';
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
            **testcase_data,
            status=SubmissionStatus.INTERNAL_ERROR,
        )
    

def execute_solution(testcase_data, sql_file_name, sql_code, time_limit):
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
        print(result.stdout)
        return {
            'user_output': result.stdout,
            'execution_time': execution_time
        }
    except subprocess.TimeoutExpired as e:
        raise JudgerException(
            **testcase_data,
            status=SubmissionStatus.TIME_LIMIT_EXCEEDED,
            message=e.stderr,
            execution_time=time_limit
        )
    except subprocess.CalledProcessError as e:
        raise JudgerException(
            **testcase_data,
            status=SubmissionStatus.RUNTIME_ERROR,
            message=e.stderr,
        )
    except Exception as e:
        raise JudgerException(
            **testcase_data,
            status=SubmissionStatus.RUNTIME_ERROR,
        )

def get_expected_output(testcase_data, object_name):
    """
    Redis cache in 24 hours
    """
    data_from_redis = redis_client.get(object_name)
    
    if data_from_redis is not None:
        print(f"Dữ liệu đã được lấy từ Redis với object_name '{object_name}'.")
        return data_from_redis.decode('utf-8')  # Giả sử dữ liệu là chuỗi

    # Nếu không có dữ liệu trong Redis, lấy từ MinIO
    try:
        # Lấy đối tượng từ MinIO
        data_from_storage = storage_helper.read_file(bucket_name=storage_helper.default_bucket_name, object_name=object_name)
        
        # Lưu dữ liệu vào Redis để sử dụng sau này
        redis_client.set(object_name, data_from_storage, ex=86400)
        print(f"Dữ liệu đã được lấy từ MinIO và lưu vào Redis với object_name '{object_name}'.")
        
        return data_from_storage
    except S3Error as exc:
        print(f"Lỗi khi lấy dữ liệu từ MinIO: {exc}")
        raise JudgerException (
            **testcase_data,
            status=SubmissionStatus.INTERNAL_ERROR
        )
        

def compare_output(testcase_data, user_output: str, expected_output: str) -> str:
    compare_status = SubmissionStatus.WRONG_ANSWER
    try:
        # expected_output = file_helper.read_file(expected_output_file_path)
        if user_output.strip() == expected_output.strip():
            compare_status = SubmissionStatus.ACCEPTED
        return compare_status
    except:
        raise JudgerException(
            **testcase_data,
            status=SubmissionStatus.INTERNAL_ERROR,
        )

def save_standart_output(standard_output_text, issue_postfix: str, language: str, testcase_index):
    object_name = f"output_issue-{issue_postfix}_lang-{language}_tc{testcase_index}.txt"
    storage_helper.upload_file_from_content(storage_helper.default_bucket_name, object_name, standard_output_text)

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


def judge_one_testcase(issue: dict, data: dict, testcase_index: int) -> None:
    try:
        user = data['user']
        issue = data['issue']
        submission = data['submission']
        target_type = data.get('type', SubmissionStatus.TYPE_JUDGE_SUBMISSION)
        need_compare_result = target_type == SubmissionStatus.TYPE_JUDGE_SUBMISSION
        testcase = issue['testcases'][testcase_index]
        testcase_data = {
            'issue_id': issue.get('id', None),
            'lang': 'mysql',
            'testcase_id': testcase.get('id', None),
            'submission_id': submission.get('id', None),
        }

        uuid4 = uuid.uuid4()
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        db_name = user['username'] + current_time + '_' + str(uuid4)[:10].replace('-', '_')

        create_isolated_database(testcase_data, db_name)

        solution_code = f"""
        USE {db_name};
        {testcase['input_judge_sql']}
        {submission['user_sql']}
        {issue['check_judge_sql']}
        """

        solution_file_name = db_name + '.sql'
        execution_result = execute_solution(testcase_data, os.path.join(os.getenv('SOLUTION_DIR'), solution_file_name), solution_code, issue['time_limit'])
        # print(f"Thời gian thực thi truy vấn: {execution_result['execution_time']:.6f} giây")
        if need_compare_result:
            testcase['output_file_path'] = f"output_issue-{issue['code']}_lang-mysql_tc{testcase_index}.txt"
            # compare_status = compare_output(execution_result['user_output'], os.path.join(os.getenv('EXPECTED_OUTPUT_DIR'), testcase['output_file_path']))
            expected_output = get_expected_output(testcase_data, object_name=testcase['output_file_path'])
            compare_status = compare_output(testcase_data, execution_result['user_output'], expected_output)
            raise JudgerException(
                **testcase_data,
                status=compare_status,
                execution_time=execution_result['execution_time'],
                user_output=execution_result['user_output'],
                expected_output=expected_output,
            )
        else:
            if data.get('save_standart_output', False):
                save_standart_output(execution_result['user_output'], issue_postfix=issue['code'], language='mysql', testcase_index=testcase_index)
            # else:
            print(type(execution_result['execution_time']))
            raise JudgerException(
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
            file_helper.delete_file(os.path.join(os.getenv('SOLUTION_DIR'), solution_file_name))
        except:
            pass
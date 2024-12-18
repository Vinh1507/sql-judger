from db_connections import ms_sql_server_connection
import uuid
import time
from dotenv import load_dotenv
import mysql.connector
import subprocess
from datetime import datetime
import json
import os
import helpers.file_helper as file_helper
from exceptions.judger_exception import JudgerException
from constants.submission_constants import SubmissionStatus
import helpers.storage_helper as storage_helper
import redis
from minio import Minio
from minio.error import S3Error

load_dotenv()

redis_client = redis.StrictRedis(host='redis_judger', port=6379, db=0)

def create_isolated_database(test_case_data, db_name):
    try:
        sql_commands = [
            f"""
            CREATE DATABASE [{db_name}];""",
            f"""
            USE [{db_name}];
            CREATE USER [{os.getenv('DB_S2_USERNAME')}] FOR LOGIN [{os.getenv('DB_S2_USERNAME')}];
            GRANT ALTER, INSERT, DELETE, UPDATE, SELECT, REFERENCES, CREATE TABLE TO [{os.getenv('DB_S2_USERNAME')}];
            """
        ]
        
        s1_connection, s1_cursor = ms_sql_server_connection.get_s1_connection_and_cursor()
        # for command in sql_commands.split(';'):
        #     if command.strip():
        for sql in sql_commands:
            s1_cursor.execute(sql)
            s1_connection.commit()
        


    except Exception as e:
        print(e)
        raise JudgerException(
            **test_case_data,
            status=SubmissionStatus.INTERNAL_ERROR,
        )
    
def execute_input_code(test_case_data, sql_file_name, sql_code, db_name):
    try:
        file_helper.create_file(sql_file_name, sql_code)
        command = (
            f"/opt/mssql-tools/bin/sqlcmd -S {os.getenv('MS_SQL_SERVER_DB_HOST')},1433 "
            f"-U {os.getenv('DB_S2_USERNAME')} -P {os.getenv('DB_S2_PASSWORD')} -d '{db_name}' "
            f"-C -Q \"{sql_code}\""
        )
        
        
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
        )

        # print(result)

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
            message=e.__str__()
        )
        
def execute_solution(test_case_data, sql_file_name, sql_code, time_limit, db_name):
    try:
        start_time = time.time()
        file_helper.create_file(sql_file_name, sql_code)
        command = (
            f"/opt/mssql-tools/bin/sqlcmd -S {os.getenv('MS_SQL_SERVER_DB_HOST')},1433 "
            f"-U {os.getenv('DB_S2_USERNAME')} -P {os.getenv('DB_S2_PASSWORD')} -d '{db_name}' "
            f"-C -Q \"{sql_code}\" -W"
        )
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

def remove_isolated_database(db_name):
    try:
        sql_commands = f"""
        USE master;
        DROP DATABASE {db_name};
        """
        s1_connection, s1_cursor = ms_sql_server_connection.get_s1_connection_and_cursor()
        s1_cursor.execute(sql_commands)
        s1_connection.commit()
    except:
        pass


def judge_one_test_case(data: dict, test_case_index: int) -> None:
    try:
        user = data['user']
        question = data['question']
        submission = data['submission']
        target_type = data.get('type', SubmissionStatus.TYPE_JUDGE_SUBMISSION)
        need_compare_result = target_type == SubmissionStatus.TYPE_JUDGE_SUBMISSION
        test_case = question['test_cases'][test_case_index]
        test_case_data = {
            'question_id': question.get('id', None),
            'lang': 'sql_server',
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
        {test_case['input']['text']}
        """
        input_file_name = db_name + '_input' + '.sql'
        execute_input_code(test_case_data, os.path.join(os.getenv('SOLUTION_DIR'), input_file_name), input_code, db_name)

        solution_code = f"""
        {submission['user_sql']}
        {question['additional_check_code']}
        """

        solution_file_name = db_name + '.sql'
        execution_result = execute_solution(test_case_data, os.path.join(os.getenv('SOLUTION_DIR'), solution_file_name), solution_code, question['time_limit'], db_name)
        # print(f"Thời gian thực thi truy vấn: {execution_result['execution_time']:.6f} giây")
        if need_compare_result:
            expected_output = test_case['output']['text']
            compare_status = compare_output(test_case_data, execution_result['user_output'], expected_output)
            raise JudgerException(
                **test_case_data,
                status=compare_status,
                execution_time=execution_result['execution_time'],
                user_output='', # Not response user output when judging
                expected_output='', # Not response expected output when judging
            )
        else:
            user_output = execution_result['user_output'] # Response the user output shortly, if it's too long, the process can down because of the heavy message
            if len(user_output) > 100:
                user_output = user_output[:100] + '.........(continue)..........'
            raise JudgerException(
                **test_case_data,
                status=SubmissionStatus.VALID,
                execution_time=execution_result['execution_time'],
                user_output=user_output,
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
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

load_dotenv()

def create_isolated_database(db_name):
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
        raise JudgerException(
            status='IR',
            message='',
        )
    

def execute_solution(sql_file_name, sql_code, time_limit):
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
        return {
            'user_output': result.stdout,
            'execution_time': execution_time
        }
    except subprocess.TimeoutExpired as e:
        raise JudgerException(
            status='TLE',
            message=e.stderr,
            execution_time=time_limit
        )
    except subprocess.CalledProcessError as e:
        raise JudgerException(
            status='RTE',
            message=e.stderr,
            # execution_time=execution_time
        )

def compare_output(user_output: str, expected_output_file_path: str) -> str:
    # print(user_output)
    compare_status = 'WA'
    try:
        expected_output = file_helper.read_file(expected_output_file_path)
        # file_helper.create_file(expected_output_file_path, expected_output)
        # print(len(user_output), len(expected_output))
        if user_output.strip() == expected_output.strip():
            compare_status = 'AC'
        return compare_status
    except:
        raise JudgerException(
            status='IR',
            message=''
        )

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
    
    
def judge_one_testcase(issue: dict, data: dict, testcase: dict) -> None:
    try:
        user = data['user']
        issue = data['issue']
        submission = data['submission']
        uuid4 = uuid.uuid4()
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        db_name = user['username'] + '_' + str(current_time) + '_' + str(uuid4).replace('-', '_')
        
        create_isolated_database(db_name)

        solution_code = f"""
        USE {db_name};
        {testcase['input_judge_sql']}
        {submission['user_sql']}
        {issue['check_judge_sql']}
        """

        solution_file_name = db_name + '.sql'
        execution_result = execute_solution(os.path.join(os.getenv('SOLUTION_DIR'), solution_file_name), solution_code, issue['time_limit'])
        # print(f"Thời gian thực thi truy vấn: {execution_result['execution_time']:.6f} giây")
        compare_status = compare_output(execution_result['user_output'], os.path.join(os.getenv('EXPECTED_OUTPUT_DIR'), testcase['output_file_path']))
        raise JudgerException(
            status=compare_status,
            execution_time=execution_result['execution_time']
        )
        # remove_isolated_database(db_name)
        # file_helper.delete_file(os.path.join(os.getenv('SOLUTION_DIR'), solution_file_name))
    except JudgerException as e:
        print("STATUS", e.status, e.message)
        raise e
    finally:
        try:
            remove_isolated_database(db_name)
            file_helper.delete_file(os.path.join(os.getenv('SOLUTION_DIR'), solution_file_name))
        except:
            pass
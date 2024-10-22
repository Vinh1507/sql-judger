import db_connection
import uuid
import time

import mysql.connector
 
def create_isolated_database(db_name):
    create_db_query = f"CREATE DATABASE {db_name}"
    s1_connection, s1_cursor = db_connection.get_s1_connection_and_cursor()
    s1_cursor.execute(create_db_query)
    s1_connection.commit()

def get_temp_conn_and_cursor(db_name):
    temp_config = {
        'user': 'sql_lab_s2',        # Thay thế bằng tên người dùng của bạn
        'password': 'SqlLab2024!',    # Thay thế bằng mật khẩu của bạn
        'host': 'localhost',       # Địa chỉ máy chủ (có thể là địa chỉ IP hoặc localhost)
        'database': db_name, # Thay thế bằng tên cơ sở dữ liệu của bạn
        'port': 3309
    }
    temp_connection = mysql.connector.connect(**temp_config)
    temp_cursor = temp_connection.cursor()
    return temp_connection, temp_cursor

def run_solution(temp_connection, temp_cursor, sql_statement):
    commands = [cmd.strip() for cmd in sql_statement.split(';') if cmd.strip()]
    for command in commands:
        temp_cursor.execute(command)
    results = temp_cursor.fetchall()
    temp_connection.commit()
    print(results)
    # temp_connection.close()

def remove_isolated_database(db_name):
    try:
        create_db_query = f"DROP DATABASE {db_name}"
        s1_connection, s1_cursor = db_connection.get_s1_connection_and_cursor()
        s1_cursor.execute(create_db_query)
        s1_connection.commit()
    except:
        print('Error when removing isolated database')
    
    
def judge_one_testcase(issue: dict, testcase: dict):
    uuid4 = uuid.uuid4()
    db_name = testcase['db_name']
    start_time = time.time()
    create_isolated_database(db_name)

    temp_connection, temp_cursor = get_temp_conn_and_cursor(db_name)

    solution_statement = f"""
    {testcase['input_judge_sql']};
    {issue['user_sql']}
    """
    run_solution(temp_connection, temp_cursor, solution_statement)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Thời gian thực thi truy vấn: {execution_time:.6f} giây")
    
    temp_connection.close()
    remove_isolated_database(db_name)
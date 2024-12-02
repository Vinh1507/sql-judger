import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


# Thiết lập thông tin kết nối
s1_config = {
    'user': os.getenv('DB_S1_USERNAME'),        
    'password': os.getenv('DB_S1_PASSWORD'),    
    'host': os.getenv('MYSQL_DB_HOST'),       
    # 'database': None,
    'port': os.getenv('MYSQL_DB_PORT', 3306)
}

s2_config = {
    'user': os.getenv('DB_S2_USERNAME'),        
    'password': os.getenv('DB_S1_PASSWORD'),    
    'host': os.getenv('MYSQL_DB_HOST'),       
    'database': 'base_question_data', 
    'port': os.getenv('MYSQL_DB_PORT', 3306)
}

s1_connection = None
s1_cursor = None
s2_connection = None
s2_cursor = None


def get_s1_connection_and_cursor(reopen=False):
    try:
        global s1_connection, s1_cursor   
        if s1_connection is not None:
            return s1_connection, s1_cursor
        s1_connection = mysql.connector.connect(**s1_config)
        s1_cursor = s1_connection.cursor()
        return s1_connection, s1_cursor
    except mysql.connector.Error as err:
        print(f"Đã xảy ra lỗi: {err}")
        return None, None

def get_s2_connection_and_cursor(reopen=False):
    try:
        global s2_connection, s2_cursor
        if s2_connection is not None:
            return s2_connection, s2_cursor
        s2_connection = mysql.connector.connect(**s2_config)
        s2_cursor = s2_connection.cursor()
        return s2_connection, s2_cursor
    except mysql.connector.Error as err:
        print(f"Đã xảy ra lỗi: {err}")
        return None, None


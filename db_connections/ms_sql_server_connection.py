import pymssql
from dotenv import load_dotenv
import os

load_dotenv()

# Thiết lập thông tin kết nối cho SQL Server
s1_config = {
    'server': os.getenv('MS_SQL_SERVER_DB_HOST'),       
    'database': None,            
    'username': os.getenv('DB_S1_USERNAME'),    
    'password': os.getenv('DB_S1_PASSWORD'),   
    'port': int(os.getenv('MS_SQL_SERVER_DB_BASE_PORT'))                 
}

s2_config = {
    'server': os.getenv('MS_SQL_SERVER_DB_HOST'),       
    'database': os.getenv('DB_S2_NAME'), 
    'username': os.getenv('DB_S2_USERNAME'),    
    'password': os.getenv('DB_S2_PASSWORD'),   
    'port': int(os.getenv('MS_SQL_SERVER_DB_BASE_PORT'))                   
}

s1_connection = None
s1_cursor = None
s2_connection = None
s2_cursor = None


def get_s1_connection_and_cursor(reopen=False):
    try:
        global s1_connection, s1_cursor
        if s1_connection is not None and not reopen:
            return s1_connection, s1_cursor

        # Kết nối tới SQL Server sử dụng pymssql
        s1_connection = pymssql.connect(
            server=s1_config['server'],
            user=s1_config['username'],
            password=s1_config['password'],
            database=s1_config['database'],
            port=s1_config['port']
        )
        s1_connection.autocommit(True)
        s1_cursor = s1_connection.cursor()
        return s1_connection, s1_cursor
    except pymssql.Error as err:
        print(f"Đã xảy ra lỗi: {err}")
        return None, None


def get_s2_connection_and_cursor(reopen=False):
    try:
        global s2_connection, s2_cursor
        if s2_connection is not None and not reopen:
            return s2_connection, s2_cursor

        # Kết nối tới SQL Server sử dụng pymssql
        s2_connection = pymssql.connect(
            server=s2_config['server'],
            user=s2_config['username'],
            password=s2_config['password'],
            database=s2_config['database'],
            port=s2_config['port']
        )
        s2_connection.autocommit(True)

        s2_cursor = s2_connection.cursor()
        return s2_connection, s2_cursor
    except pymssql.Error as err:
        print(f"Đã xảy ra lỗi: {err}")
        return None, None

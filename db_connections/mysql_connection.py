import mysql.connector
from dotenv import load_dotenv
import os
import time
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


def get_s1_connection_and_cursor(reopen=False, max_retries=5, retry_delay=2):
    attempts = 0
    while attempts < max_retries:
        try:
            global s1_connection, s1_cursor
            # Nếu đã có kết nối, trả về kết nối và cursor hiện tại
            if s1_connection and not reopen:
                return s1_connection, s1_cursor
            
            # Thử kết nối MySQL
            s1_connection = mysql.connector.connect(**s1_config)
            s1_cursor = s1_connection.cursor()
            return s1_connection, s1_cursor
        except mysql.connector.Error as err:
            print(f"Đã xảy ra lỗi: {err}, thử lại lần {attempts + 1} trong {retry_delay} giây...")
            attempts += 1
            time.sleep(retry_delay)
    
    # Nếu thử hết số lần mà vẫn không kết nối được, trả về None
    print("Không thể kết nối sau nhiều lần thử.")
    return None, None

def get_s2_connection_and_cursor(reopen=False, max_retries=5, retry_delay=2):
    attempts = 0
    while attempts < max_retries:
        try:
            global s2_connection, s2_cursor
            # Nếu đã có kết nối, trả về kết nối và cursor hiện tại
            if s2_connection and not reopen:
                return s2_connection, s2_cursor
            
            # Thử kết nối MySQL
            s2_connection = mysql.connector.connect(**s2_config)
            s2_cursor = s2_connection.cursor()
            return s2_connection, s2_cursor
        except mysql.connector.Error as err:
            print(f"Đã xảy ra lỗi: {err}, thử lại lần {attempts + 1} trong {retry_delay} giây...")
            attempts += 1
            time.sleep(retry_delay)
    
    # Nếu thử hết số lần mà vẫn không kết nối được, trả về None
    print("Không thể kết nối sau nhiều lần thử.")
    return None, None
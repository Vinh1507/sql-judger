import mysql.connector

# Thiết lập thông tin kết nối
s1_config = {
    'user': 'sql_lab_s1',        # Thay thế bằng tên người dùng của bạn
    'password': 'SqlLab2024!',    # Thay thế bằng mật khẩu của bạn
    'host': 'localhost',       # Địa chỉ máy chủ (có thể là địa chỉ IP hoặc localhost)
    # 'database': 'base_issue_data', # Thay thế bằng tên cơ sở dữ liệu của bạn
    'port': 3309
}

s2_config = {
    'user': 'sql_lab_s2',        # Thay thế bằng tên người dùng của bạn
    'password': 'SqlLab2024!',    # Thay thế bằng mật khẩu của bạn
    'host': 'localhost',       # Địa chỉ máy chủ (có thể là địa chỉ IP hoặc localhost)
    'database': 'base_issue_data', # Thay thế bằng tên cơ sở dữ liệu của bạn
    'port': 3309
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


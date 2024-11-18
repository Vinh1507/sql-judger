import pymssql

# Thiết lập thông tin kết nối cho SQL Server
s1_config = {
    'server': 'sqlserver',        # Địa chỉ máy chủ hoặc tên server
    'database': None,             # Tên cơ sở dữ liệu (None nếu chưa cần)
    'username': 'sql_lab_s1',     # Tên người dùng
    'password': 'SqlLab2024!',    # Mật khẩu
    'port': 1433                  # Cổng (1433 mặc định cho SQL Server)
}

s2_config = {
    'server': 'sqlserver',        # Địa chỉ máy chủ hoặc tên server
    'database': 'base_question_data',  # Tên cơ sở dữ liệu
    'username': 'sql_lab_s2',     # Tên người dùng
    'password': 'SqlLab2024!',    # Mật khẩu
    'port': 1433                  # Cổng (1433 mặc định cho SQL Server)
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

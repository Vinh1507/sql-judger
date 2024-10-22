import os

def create_file(file_name, sql_code):
    with open(file_name, 'w') as file:
        file.write(sql_code)
        # print(f"Đã tạo file {file_name} và ghi nội dung vào.")

def read_file(filepath):
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"File '{filepath}' không tồn tại.")
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

def delete_file(filepath):
    try:
        os.remove(filepath)
        # print(f"File '{filepath}' đã được xóa thành công.")
    except FileNotFoundError:
        print(f"File '{filepath}' không tồn tại.")
    except PermissionError:
        print(f"Không có quyền xóa file '{filepath}'.")
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
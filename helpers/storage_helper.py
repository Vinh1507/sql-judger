from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv
import io

from zipfile import ZipFile
import re
import redis
import json

load_dotenv()

client = Minio(
    os.getenv('S3_ENDPOINT'), 
    access_key=os.getenv('S3_ACCESS_KEY'), 
    secret_key=os.getenv('S3_SECRET_KEY'), 
    secure=(os.getenv('S3_SECURE') == 'True')
)
redis_client = redis.StrictRedis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=int(os.getenv('REDIS_DB')))

default_bucket_name = os.getenv('MINIO_DEFAULT_BUCKET_NAME', "sql-data")

# Create bucket if not exist
def create_bucket(bucket_name):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' đã được tạo.")

def upload_file_from_content(bucket_name, object_name, content):
    try:
        # Chuyển đổi chuỗi thành một stream (BytesIO)
        content_bytes = io.BytesIO(content.encode("utf-8"))
        content_length = len(content_bytes.getvalue())

        # Upload stream lên MinIO
        client.put_object(
            bucket_name, object_name, content_bytes, content_length, content_type="text/plain"
        )
        print(f"Nội dung đã được tải lên MinIO dưới dạng object '{object_name}'.")
        
    except S3Error as exc:
        print(f"Lỗi khi upload nội dung: {exc}")

# Upload file
def upload_file(bucket_name, file_path, object_name):
    try:
        client.fput_object(bucket_name, object_name, file_path)
        print(f"File '{object_name}' đã được tải lên MinIO.")
    except S3Error as exc:
        print(f"Lỗi khi tải lên file: {exc}")

# Download file
def download_file(bucket_name, object_name, file_path):
    try:
        client.fget_object(bucket_name, object_name, file_path)
        print(f"File '{object_name}' đã được tải xuống từ MinIO.")
    except S3Error as exc:
        print(f"Lỗi khi tải xuống file: {exc}")

def read_file(bucket_name, object_name):
    print(object_name)
    try:
        response = client.get_object(bucket_name, object_name)
        
        content = response.read().decode("utf-8") 
        # print(f"Nội dung file '{object_name}':\n{content}")
        
        # Close stream after reading file
        response.close()
        response.release_conn()
        return content
    except S3Error as exc:
        print(f"Lỗi khi đọc file: {exc}")

def read_input_zip_file(bucket_name, zip_file_path):
    try:
        data_from_redis = redis_client.get(zip_file_path)
        if data_from_redis is not None:
            return json.loads(data_from_redis.decode('utf-8'))
        
        txt_files_content = []
        response = client.get_object(bucket_name, zip_file_path)
        with ZipFile(io.BytesIO(response.read())) as zip_file:
            # Lọc các file có tên bắt đầu bằng 'input' và kết thúc bằng '.txt'
            txt_files = [file_info for file_info in zip_file.infolist() if file_info.filename.startswith("input") and file_info.filename.endswith(".txt")]
            
            # Sắp xếp các file dựa trên số trong tên file
            txt_files.sort(key=lambda x: int(re.search(r"input(\d+)\.txt", x.filename).group(1)))

            # Đọc nội dung từng file .txt và lưu vào mảng theo thứ tự đã sắp xếp
            for file_info in txt_files:
                with zip_file.open(file_info) as txt_file:
                    content = txt_file.read().decode("utf-8")
                    txt_files_content.append({
                        "file_name": file_info.filename,
                        "text": content,
                    })

        # # In nội dung các file .txt đã đọc
        # for index, content in enumerate(txt_files_content, start=1):
        #     print(f"File {index} content:\n{content}\n")
        redis_client.set(zip_file_path, json.dumps(txt_files_content), ex=86400)
        return txt_files_content
    except Exception as e:
        print(e)
        return None

def read_output_zip_file(bucket_name, zip_file_path):
    try:
        data_from_redis = redis_client.get(zip_file_path)
        if data_from_redis is not None:
            return json.loads(data_from_redis.decode('utf-8'))
        
        txt_files_content = []
        response = client.get_object(bucket_name, zip_file_path)
        with ZipFile(io.BytesIO(response.read())) as zip_file:
            # Lọc các file có tên bắt đầu bằng 'output' và kết thúc bằng '.txt'
            txt_files = [file_info for file_info in zip_file.infolist() if file_info.filename.startswith("output") and file_info.filename.endswith(".txt")]
            
            # Sắp xếp các file dựa trên số trong tên file
            txt_files.sort(key=lambda x: int(re.search(r"output(\d+)\.txt", x.filename).group(1)))

            # Đọc nội dung từng file .txt và lưu vào mảng theo thứ tự đã sắp xếp
            for file_info in txt_files:
                with zip_file.open(file_info) as txt_file:
                    content = txt_file.read().decode("utf-8")
                    txt_files_content.append({
                        "file_name": file_info.filename,
                        "text": content,
                    })

        # In nội dung các file .txt đã đọc
        # for index, content in enumerate(txt_files_content, start=1):
        #     print(f"File {index} content:\n{content}\n")
        redis_client.set(zip_file_path, json.dumps(txt_files_content), ex=86400)
        return txt_files_content
    except Exception as e:
        print(e)
        return None


def upload_output_zip_file(bucket_name, zip_file_path, user_outputs):
    print(user_outputs)
    try:
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            # Tạo từng file output và thêm vào zip
            for user_output in user_outputs:
                file_number = int(re.search(r"input(\d+)\.txt", user_output['test_case']['input_file_name']).group(1))
                file_name = f"output{file_number}.txt"
                content = user_output['test_case']['output_text']
                zip_file.writestr(file_name, content)
        # Thiết lập lại con trỏ buffer về đầu trước khi gửi lên MinIO
        zip_buffer.seek(0)
        client.put_object(
            bucket_name,
            zip_file_path,
            data=zip_buffer,
            length=zip_buffer.getbuffer().nbytes,
            content_type="application/zip"
        )
        return True
    except Exception as e:
        print(e)
        return False

def upload_input_zip_file(bucket_name, zip_file_path, test_cases):
    try:
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            # Tạo từng file output và thêm vào zip
            for test_case in test_cases:
                input = test_case['input']
                file_name = input['file_name']
                content = input['text']
                zip_file.writestr(file_name, content)
        # Thiết lập lại con trỏ buffer về đầu trước khi gửi lên MinIO
        zip_buffer.seek(0)
        client.put_object(
            bucket_name,
            zip_file_path,
            data=zip_buffer,
            length=zip_buffer.getbuffer().nbytes,
            content_type="application/zip"
        )
        return True
    except Exception as e:
        print(e)
        return False
# upload_file("/home/vinh/Documents/mysql-judger/expected_output/tc2.txt", "file.txt")
# read_file("file.txt")
# download_file("file.txt", "/home/vinh/Documents/mysql-judger/expected_output/down2.txt")


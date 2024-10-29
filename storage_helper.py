from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv
import io

load_dotenv()

client = Minio(
    os.getenv('S3_ENDPOINT'), 
    access_key=os.getenv('S3_ACCESS_KEY'), 
    secret_key=os.getenv('S3_SECRET_KEY'), 
    secure=(os.getenv('S3_SECURE') == 'True')
)

default_bucket_name = "sql-data"

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

# upload_file("/home/vinh/Documents/mysql-judger/expected_output/tc2.txt", "file.txt")
# read_file("file.txt")
# download_file("file.txt", "/home/vinh/Documents/mysql-judger/expected_output/down2.txt")


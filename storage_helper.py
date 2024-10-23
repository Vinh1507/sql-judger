from minio import Minio
from minio.error import S3Error

client = Minio(
    "localhost:9000", 
    access_key="vinhbh", 
    secret_key="1234567abc", 
    secure=False 
)

bucket_name = "sql-data"

# Create bucket if not exist
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)
    print(f"Bucket '{bucket_name}' đã được tạo.")

# Upload file
def upload_file(file_path, object_name):
    try:
        client.fput_object(bucket_name, object_name, file_path)
        print(f"File '{object_name}' đã được tải lên MinIO.")
    except S3Error as exc:
        print(f"Lỗi khi tải lên file: {exc}")

# Download file
def download_file(object_name, file_path):
    try:
        client.fget_object(bucket_name, object_name, file_path)
        print(f"File '{object_name}' đã được tải xuống từ MinIO.")
    except S3Error as exc:
        print(f"Lỗi khi tải xuống file: {exc}")

def read_file(object_name):
    try:
        response = client.get_object(bucket_name, object_name)
        
        content = response.read().decode("utf-8") 
        print(f"Nội dung file '{object_name}':\n{content}")
        
        # Close stream after reading file
        response.close()
        response.release_conn()
        
    except S3Error as exc:
        print(f"Lỗi khi đọc file: {exc}")

upload_file("/home/vinh/Documents/mysql-judger/expected_output/tc2.txt", "file.txt")
read_file("file.txt")
download_file("file.txt", "/home/vinh/Documents/mysql-judger/expected_output/down.txt")


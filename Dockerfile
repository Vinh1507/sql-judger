# Sử dụng image Python làm base image
FROM python:3.11

# Cài đặt các gói cần thiết cho sqlcmd
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    ca-certificates \
    lsb-release \
    default-mysql-client \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y mssql-tools unixodbc-dev \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện Python cần thiết
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn vào container
COPY . /app

# Mở cổng nếu cần (ví dụ, cho ứng dụng web)
EXPOSE 8000

USER root
# Lệnh để chạy ứng dụng Python của bạn
CMD ["python", "consumer.py"]

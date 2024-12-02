# sql-judger

```
docker compose up
python consumer.py

```


sudo apt-get update

# Cài đặt các gói cần thiết
sudo apt-get install -y unixodbc-dev

# Thêm repository của Microsoft
sudo curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > sudo tee /etc/apt/sources.list.d/mssql-release.list

# Cập nhật lại repository
sudo apt-get update

# Cài đặt ODBC Driver 17 for SQL Server
sudo apt-get install -y msodbcsql17
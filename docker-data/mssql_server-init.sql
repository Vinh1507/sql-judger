USE [master];

-- Tạo người dùng sql_lab_s1
CREATE LOGIN sql_lab_s1 WITH PASSWORD = 'SqlLab2024!';
CREATE USER sql_lab_s1 FOR LOGIN sql_lab_s1;
EXEC sp_addsrvrolemember 'sql_lab_s1', 'sysadmin';

-- Tạo người dùng sql_lab_s2
CREATE LOGIN sql_lab_s2 WITH PASSWORD = 'SqlLab2024!';
CREATE USER sql_lab_s2 FOR LOGIN sql_lab_s2;
-- GRANT ALTER, CREATE, INSERT, UPDATE, DELETE, SELECT, EXECUTE ON SCHEMA::dbo TO sql_lab_s2;

-- -- Tạo người dùng sql_lab_s3
-- CREATE LOGIN sql_lab_s3 WITH PASSWORD = 'SqlLab2024!';
-- CREATE USER sql_lab_s3 FOR LOGIN sql_lab_s3;
-- GRANT CREATE, INSERT, UPDATE, DELETE, SELECT ON DATABASE::[master] TO sql_lab_s3;
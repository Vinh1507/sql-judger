
        CREATE DATABASE [admin2024_11_18_03_42_29_7cdf7f8a_6];
        GO
        USE [admin2024_11_18_03_42_29_7cdf7f8a_6];
        GO
        CREATE USER [sql_lab_s2] FOR LOGIN [sql_lab_s2];
        GO
        GRANT ALTER, INSERT, DELETE, UPDATE, SELECT, REFERENCES, CREATE TABLE TO [sql_lab_s2];
        GO
        
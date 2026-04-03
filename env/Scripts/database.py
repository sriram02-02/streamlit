import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="NewStrongPassword123",
    database="phonepe"
)

cursor = conn.cursor()
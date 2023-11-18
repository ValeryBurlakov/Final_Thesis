
import mysql.connector
from config.config import PASSWORD, HOST, USER, DATABASE


# Создайте функцию, которая будет возвращать соединение с базой данных
def create_connection():
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    return mydb


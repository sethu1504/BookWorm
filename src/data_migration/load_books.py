import pymysql
import pandas as pd

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='sethu123',
                             db='Book',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        sql = "INSERT INTO `app_book` (`title`) VALUES (%s)"
        books_data = pd.read_csv("../../data/books.csv")
        for index, row in books_data.iterrows():
            print(row["Book Title"])
            cursor.execute(sql, (row["Book Title"]))
        connection.commit()

finally:
    connection.close()
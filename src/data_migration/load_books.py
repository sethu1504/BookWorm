import pymysql
import pandas as pd
import calendar
import re

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='sethu123',
                             db='Brie',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        sql = '''INSERT INTO `app_book` (`title`, `isbn`, `author`, `language`, `pages`, `publication`, `pub_date`, 
        `pub_month`, `pub_year`, `book_url`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        books_data = pd.read_csv("../../data/batch_1/books.csv")
        month_dict = {v: k for k, v in enumerate(calendar.month_abbr)}
        for index, row in books_data.iterrows():
            title = row["Book Title"]
            print(title)

            isbn = row["ISBN"]
            author = row["Author"]
            if type(author) is float:
                author = ""
            language = row["Language"]
            if type(language) is float:
                language = ""
            pages = row["Pages"]
            if pages == "[]":
                pages = -1
            publication = row["Publication"]
            if type(publication) is float:
                publication = ""
            url = row["Book URL"]
            if type(url) is float:
                url = ""

            date_str = row["Publish Date"]

            if type(date_str) is float:
                pub_date = -1
                pub_month = -1
                pub_year = -1
            else:
                date_str_list = date_str.split(" ")
                if len(date_str_list) == 3:
                    pub_month = int(month_dict[date_str_list[0][0:3]])
                    pub_date = int(re.findall(r'\d+', date_str_list[1])[0])
                    pub_year = int(date_str_list[2])
                elif len(date_str_list) == 2:
                    pub_month = int(month_dict[date_str_list[0][0:3]])
                    pub_year = int(date_str_list[1])
                elif len(date_str_list) == 1:
                    pub_date = -1
                    pub_month = -1
                    pub_year = int(date_str_list[0])

            cursor.execute(sql, (title, isbn, author, language, pages, publication, pub_date, pub_month, pub_year, url))
            connection.commit()

finally:
    connection.close()

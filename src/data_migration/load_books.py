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
        `pub_month`, `pub_year`, `book_url`, `img_url`, `google_price`, `barnes_price`, `indie_price`, `amazon_price`, 
        `r1`, `r2`, `r3`, `r4`, `r5`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s)'''
        books_data = pd.read_csv("../../data/batch_1/books.csv")
        img_price_data = pd.read_csv("../../data/batch_1/image_and_price (1).csv")
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

            img_url = img_price_data["Book Image"][index]
            if type(img_url) is float:
                img_url = ""

            gp_price = img_price_data["Google Play"][index]
            if type(gp_price) is float or "http" in gp_price:
                gp_price = ""

            bnb_price = img_price_data["Barnes and Noble"][index]
            if type(bnb_price) is float or "http" in bnb_price:
                bnb_price = ""

            indie_price = img_price_data["Indie Bound"][index]
            if type(indie_price) is float or "http" in indie_price:
                indie_price = ""
            amazon_price = ""
            r1 = ""
            r2 = ""
            r3 = ""
            r4 = ""
            r5 = ""

            cursor.execute(sql, (title, isbn, author, language, pages, publication, pub_date, pub_month, pub_year, url,
                                 img_url, gp_price, bnb_price, indie_price, amazon_price, r1, r2, r3, r4, r5))
            connection.commit()

finally:
    connection.close()

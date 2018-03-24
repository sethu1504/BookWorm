import pymysql
from pymongo import MongoClient
import pandas as pd
from src.clean_text import give_clean_words_list

mysql_connection = pymysql.connect(host='localhost',
                                   user='root',
                                   password='sethu123',
                                   db='Brie',
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)

try:
    mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
    mongo_brie_db = mongo_client.Brie
    with mysql_connection.cursor() as cursor:
        sql_query = '''select id from app_book'''
        cursor.execute(sql_query)
        result = cursor.fetchall()

        books_desc = pd.read_csv("../../data/batch_1/description_wikipedia_readgeek.csv", encoding="ISO-8859-1")
        books = pd.read_csv("../../data/batch_1/books.csv", encoding="ISO-8859-1")
        reviews_data = pd.read_csv("../../data/batch_1/reviews_users.csv", encoding="ISO-8859-1")
        reviews_index = -1

        description_collection = mongo_brie_db.book_secondary_details
        for index, row in books_desc.iterrows():
            book_id = result[index]["id"]
            doc = dict()
            doc["id"] = book_id

            book_title = row["Book Title"]
            book_isbn = row["ISBN"]
            print(book_title)

            doc["title"] = book_title
            doc["genre"] = books["Genres"][index]

            good_reads_desc = row["GoodReads Description"]
            if type(good_reads_desc) is float:
                good_reads_desc = ""
            doc["goodreads"] = give_clean_words_list(good_reads_desc)

            wiki_desc = row["Wikipedia Description"]
            if type(wiki_desc) is float:
                wiki_desc = ""
            doc["wikipedia"] = give_clean_words_list(wiki_desc)

            read_geek_desc = row["Readgeek Description"]
            if type(read_geek_desc) is float:
                read_geek_desc = ""
            doc["readgeek"] = give_clean_words_list(read_geek_desc)

            # riffle_desc = row["Riffle Description"]
            # if type(riffle_desc) is float:
            #     riffle_desc = ""
            # doc["riffle"] = give_clean_words_list(riffle_desc)
            #
            # amazon_desc = row["Amazon Description"]
            # if type(amazon_desc) is float:
            #     amazon_desc = ""
            # doc["amazon"] = give_clean_words_list(amazon_desc)

            doc["amazon_url"] = row["Amazon URL"]
            doc["isbn"] = row["ISBN"]

            review_details_list = []
            print(reviews_index)
            while True:
                reviews_index += 1
                review_isbn = reviews_data["ISBN"][reviews_index]
                review_book_title = reviews_data["Book Title"][reviews_index]

                if review_book_title == book_title or review_isbn == book_isbn:
                    review_obj = dict()
                    review_obj["user_id"] = reviews_data["User ID"][reviews_index]
                    review_obj["user_id"] = reviews_data["User Name"][reviews_index]
                    review_obj["user_url"] = reviews_data["User URL"][reviews_index]
                    review_obj["date"] = reviews_data["Review Date"][reviews_index]
                    review_text = reviews_data["Review"][reviews_index]
                    if type(review_text) is float:
                        review_text = ""
                    review_obj["review"] = give_clean_words_list(review_text)
                    review_details_list.append(review_obj)

                else:
                    reviews_index -= 1
                    break

            doc["reviews"] = review_details_list
            print(len(review_details_list))
            description_collection.insert_one(doc)

finally:
    mysql_connection.close()
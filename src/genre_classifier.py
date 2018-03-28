from pyspark import SparkConf, SparkContext
import operator
import pandas as pd
from pymongo import MongoClient
import pyspark.sql.types as types
from pyspark.sql import SQLContext
import numpy as np
import pymysql

mysql_connection = pymysql.connect(host='localhost',
                                   user='root',
                                   password='sethu123',
                                   db='Brie',
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)

conf = SparkConf().setAppName('word count')
sc = SparkContext(conf=conf)
sqlContext = SQLContext(sc)

schema = types.StructType([types.StructField('Word', types.StringType(), False),
                           types.StructField('Count', types.IntegerType(), False),
                           types.StructField('Percent', types.FloatType(), False)])


def bags_format(line):
    contents = line.split()
    return str(contents[0]), int(contents[1]), float(contents[2])


if __name__ == '__main__':

    mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
    mongo_brie_db = mongo_client.Brie
    description_collection = mongo_brie_db.book_secondary_details

    all_books = description_collection.find(no_cursor_timeout=True)

    # data = pd.read_csv("../data/batch_1/description_wikipedia_readgeek.csv", encoding="ISO-8859-1")
    books = pd.read_csv("../data/batch_1/books.csv")

    genre_list = ["crime", "fantasy", "young-adult", "romance", "comedy", "dystopia",
                  "action", "historical", "non-fiction", "science fiction", "self-help"]
    no_of_genres = len(genre_list)

    for genre in genre_list:
        crime_words = sc.textFile('../data/word_counts/' + genre + '_counts')
        if genre == "young-adult":
            genre = 'YA'

        elif genre == "non-fiction":
            genre = "NF"

        elif genre == "science fiction":
            genre = "SF"

        elif genre == "self-help":
            genre = "SH"

        genre_bag_words = crime_words.map(bags_format)

        genre_word_df = sqlContext.createDataFrame(genre_bag_words, schema=schema).cache()

        genre_word_df.createOrReplaceTempView(genre + '_words')

    try:
        for book in all_books:
            book_id = book["id"]
            gr_desc = book["goodreads"]
            if type(gr_desc) is float:
                gr_desc = ""
            wk_desc = book["wikipedia"]
            if type(wk_desc) is float:
                wk_desc = ""
            rg_desc = book["readgeek"]
            if type(rg_desc) is float:
                rg_desc = ""
            riff_desc = book["riffle"]
            if type(riff_desc) is float:
                riff_desc = ""

            sql_query = '''select author from app_book where id=''' + str(book["id"])
            with mysql_connection.cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchone()

            author = result['author']

            tokens = gr_desc + wk_desc + rg_desc + riff_desc + author.split(" ")
            desc_tokens = sc.parallelize(tokens)

            words = desc_tokens.map(lambda w: (w, 1))
            wordcount = words.reduceByKey(operator.add)

            total_word_count = wordcount.map(lambda x: x[1]).sum()

            words_with_count_percents = wordcount.map(lambda line: (line[0], line[1], (line[1] / total_word_count)))

            df = sqlContext.createDataFrame(words_with_count_percents, schema=schema).cache()
            df.createOrReplaceTempView('description')

            genre_scores = []
            for genre in genre_list:
                if genre == "young-adult":
                    genre = 'YA'
                elif genre == "non-fiction":
                    genre = "NF"
                elif genre == "science fiction":
                    genre = "SF"
                elif genre == "self-help":
                    genre = "SH"
                common_words = sqlContext.sql('''
                                              select description.word as Word, description.Count as desc_count,''' +
                                              genre + '''_words.Count as genre_count, description.Percent as desc_percent, 
                                              ''' + genre + '''_words.Percent as genre_percent from description join 
                                              ''' + genre + '''_words on description.Word = ''' + genre + '''_words.Word
                                              ''')

                common_words.createOrReplaceTempView('common_words')

                word_score = sqlContext.sql('''
                                            select desc_percent * genre_percent as score from common_words
                                            ''')

                word_score.createOrReplaceTempView('word_score')

                genre_score = sqlContext.sql('''
                                            select sum(score) as Genre_score from word_score
                                            ''')
                genre_scores.append(genre_score.select('Genre_score').head(1)[0][0])

            print(book["title"] + "\n")
            # for i in range(0, len(genre_scores)):
            #     print(genre_list[i] + " " + str((genre_scores[i]) * 100))
            # print("\n")

            try:
                genre_scores = np.array(genre_scores)
                index_scores = np.argsort(genre_scores)
                genre_scores = np.sort(genre_scores)

            except TypeError:
                continue

            base = genre_scores[-4]
            percent_changes = []
            for i in range(0, 3):
                curr = genre_scores[no_of_genres - 1 - i]
                percent_changes.append(((curr - base) / base) * 100)
            percent_changes = np.array(percent_changes)
            base_percent = (100 - percent_changes.sum()) / 4

            genre_dict = dict()
            for i in range(0, 3):
                genre_index = index_scores[no_of_genres - 1 - i]
                genre_name = genre_list[genre_index]
                genre_value = percent_changes[i] + base_percent
                print(genre_name + " " + str(genre_value) + "%")
                genre_dict[genre_name] = genre_value
            genre_dict[genre_list[index_scores[-4]]] = base_percent
            print(genre_list[index_scores[-4]] + " " + str(base_percent) + "%\n")
            description_collection.update_one({"id": book["id"]}, {"$set": {"genre_dissect": genre_dict}}, upsert=False)

        all_books.close()

    finally:
        mysql_connection.close()





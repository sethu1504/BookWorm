from pyspark import SparkConf, SparkContext
import operator
import pandas as pd
from clean_text import give_clean_words_list
import re
import pyspark.sql.types as types
from pyspark.sql import SQLContext
import numpy as np

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
    data = pd.read_csv("../data/batch_1/description_wikipedia_readgeek.csv", encoding="ISO-8859-1")
    books = pd.read_csv("../data/batch_1/books.csv")

    genre_list = ["crime", "fantasy", "young-adult", "romance", "comedy", "dystopia",
                  "action", "historical", "non-fiction", "science fiction"]
    no_of_genres = len(genre_list)

    for genre in genre_list:
        crime_words = sc.textFile('../data/word_counts/' + genre + '_counts')
        if genre == "young-adult":
            genre = 'YA'

        elif genre == "non-fiction":
            genre = "NF"

        elif genre == "science fiction":
            genre = "SF"

        genre_bag_words = crime_words.map(bags_format)

        genre_word_df = sqlContext.createDataFrame(genre_bag_words, schema=schema).cache()

        genre_word_df.createOrReplaceTempView(genre + '_words')

    for index, row in data.iterrows():
        gr_desc = row["GoodReads Description"]
        if type(gr_desc) is float:
            gr_desc = ""
        wk_desc = row["Wikipedia Description"]
        if type(wk_desc) is float:
            wk_desc = ""
        rg_desc = row["Readgeek Description"]
        if type(rg_desc) is float:
            rg_desc = ""

        # rg_desc = re.sub("[^a-zA-Z]", "", str(rg_desc))

        author = books["Author"][index]

        tokens = give_clean_words_list(gr_desc) + give_clean_words_list(wk_desc) + give_clean_words_list(rg_desc) + \
            author.split(" ")
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

        print(row["Book Title"] + "\n")
        # for i in range(0, len(genre_scores)):
        #     print(genre_list[i] + " " + str((genre_scores[i]) * 100))
        # print("\n")

        genre_scores = np.array(genre_scores)
        index_scores = np.argsort(genre_scores)
        genre_scores = np.sort(genre_scores)

        base = genre_scores[-4]
        percent_changes = []
        for i in range(0, 3):
            curr = genre_scores[no_of_genres - 1 - i]
            percent_changes.append(((curr - base) / base) * 100)
        percent_changes = np.array(percent_changes)
        base_percent = (100 - percent_changes.sum()) / 4
        for i in range(0, 3):
            genre_index = index_scores[no_of_genres - 1 - i]
            print(genre_list[genre_index] + " " + str(percent_changes[i] + base_percent) + "%")
        print(genre_list[index_scores[-4]] + " " + str(base_percent) + "%\n")
        # print("Other 10%\n")




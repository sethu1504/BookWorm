from pyspark import SparkConf, SparkContext
import operator
import pandas as pd
from clean_text import give_clean_words_list
import pyspark.sql.types as types
from pyspark.sql import SQLContext

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
    data = pd.read_csv("../data/description.csv")

    genre_list = ["crime", "fiction", "fantasy", "young-adult", "romance", "comedy", "dystopia",
                  "action", "historical", "non-fiction"]

    for genre in genre_list:
        crime_words = sc.textFile('../data/word_counts/' + genre + '_counts')
        if genre == "young-adult":
            genre = 'YA'

        elif genre == "non-fiction":
            genre = "NF"

        genre_bag_words = crime_words.map(bags_format)

        genre_word_df = sqlContext.createDataFrame(genre_bag_words, schema=schema).cache()

        genre_word_df.createOrReplaceTempView(genre + '_words')

    for index, row in data.iterrows():
        desc = row["GoodReads Description"]

        desc_tokens = sc.parallelize(give_clean_words_list(desc))

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
        total_score = sum(genre_scores)
        for i in range(0, len(genre_scores)):
            print(genre_list[i] + " " + str((genre_scores[i]) * 100))
        print("\n")


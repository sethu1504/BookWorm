import pandas as pd
import calendar
import re
import csv
import codecs
from src.clean_text import give_clean_words_list
import pyspark.sql.types as types
from pyspark.sql import SQLContext
from pyspark import SparkConf, SparkContext
import numpy as np
import operator
from collections import defaultdict


def bags_format(line):
    contents = line.split()
    return str(contents[0]), int(contents[1]), float(contents[2])

conf = SparkConf().setAppName('word count')
sc = SparkContext(conf=conf)
sqlContext = SQLContext(sc)

schema = types.StructType([types.StructField('Word', types.StringType(), False),
                           types.StructField('Count', types.IntegerType(), False),
                           types.StructField('Percent', types.FloatType(), False)])

genre_list = ["crime", "fantasy", "young-adult", "romance", "comedy", "dystopia",
              "action", "historical", "non-fiction", "science fiction", "self-help"]
no_of_genres = len(genre_list)

for genre in genre_list:
    crime_words = sc.textFile('../../data/word_counts/' + genre + '_counts')
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

# Input Files
books_data = pd.read_csv("../../data/batch_1/books.csv")
img_price_data = pd.read_csv("../../data/batch_1/image_and_price.csv")
desc_data = pd.read_csv("../../data/batch_1/description_all.csv")
amazon_data = pd.read_csv("../../data/batch_1/amazon.csv")
reviews_data = pd.read_csv("../../data/batch_1/reviews_users.csv")

# Created Files
out = csv.writer(codecs.open("../../data/batch_1/final_1.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)

out.writerow(["ID", "Book Title", "ISBN", "Rating", "Author", "Language", "Pages", "Publication", "Publish Date",
              "Publish Month", "Publish Year", "Genres", "Image", "Google Play", "Google Play URL", "Barnes and Noble",
              "Barnes and Noble URL", "Indie Bound", "Indie Bound URL",
              "Amazon", "Amazon URL", "R1", "R1 URL", "R2", "R2 URL", "R3", "R3 URL", "R4", "R4 URL", "R5", "R5 URL",
              "GoodReads_Description", "Wiki_Description", "Readgeek_Description", "Riffle_Description",
              "Amazon_Description", "crime", "fantasy", "young-adult", "romance", "comedy", "dystopia", "action",
              "historical", "non-fiction", "science fiction", "self-help"])

out_user_review = csv.writer(codecs.open("../../data/batch_1/final_2.csv", "w", "utf-8"), delimiter=",",
                             quoting=csv.QUOTE_ALL)
out_user_review.writerow(["ID", "Book Title", "ISBN", "User ID", "User Name", "User URL", "Rating",
                          "Review Data", "Review"])

book_id = 100000 - 1
reviews_index = -1
month_dict = {v: k for k, v in enumerate(calendar.month_abbr)}
for index, row in books_data.iterrows():
    book_id += 1
    title = row["Book Title"]
    print(str(index) + " " + title)

    # Books CSV data
    isbn = row["ISBN"]
    rating = row["Rating"]
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

    genres = row["Genres"]
    if type(genres) is float:
        genres = ""

    # Image Price data
    img_url = img_price_data["Book Image"][index]
    if type(img_url) is float:
        img_url = ""

    gp_price = img_price_data["Google Play"][index]
    if type(gp_price) is float or "http" in gp_price:
        gp_price = ""
    gp_url = img_price_data["Google Play URL"][index]
    if type(gp_url) is float:
        gp_url = ""

    bnb_price = img_price_data["Barnes and Noble"][index]
    if type(bnb_price) is float or "http" in bnb_price:
        bnb_price = ""
    bnb_url = img_price_data["Barnes and Noble URL"][index]
    if type(bnb_url) is float:
        bnb_url = ""

    indie_price = img_price_data["Indie Bound"][index]
    if type(indie_price) is float or "http" in indie_price:
        indie_price = ""
    indie_url = img_price_data["Indie Bound URL"][index]
    if type(indie_url) is float:
        indie_url = ""

    # Amazon Data
    amazon_price = amazon_data["Amazon Price"][index]
    if type(amazon_price) is float or "http" in amazon_price:
        amazon_price = ""

    r1 = amazon_data["R1 Title"][index]
    if type(r1) is float:
        r1 = ""
    r1_url = amazon_data["R1 URL"][index]
    if type(r1_url) is float:
        r1_url = ""

    r2 = amazon_data["R2 Title"][index]
    if type(r2) is float:
        r2 = ""
    r2_url = amazon_data["R2 URL"][index]
    if type(r2_url) is float:
        r2_url = ""

    r3 = amazon_data["R3 Title"][index]
    if type(r3) is float:
        r3 = ""
    r3_url = amazon_data["R3 URL"][index]
    if type(r3_url) is float:
        r3_url = ""

    r4 = amazon_data["R4 Title"][index]
    if type(r4) is float:
        r4 = ""
    r4_url = amazon_data["R4 URL"][index]
    if type(r4_url) is float:
        r4_url = ""

    r5 = amazon_data["R5 Title"][index]
    if type(r5) is float:
        r5 = ""
    r5_url = amazon_data["R5 URL"][index]
    if type(r5_url) is float:
        r5_url = ""

    amazon_url = amazon_data["Book URL"][index]
    if type(amazon_url) is float:
        amazon_url = ""

    # Description data

    good_reads_desc = desc_data["GoodReads Description"][index]
    if type(good_reads_desc) is float:
        good_reads_desc = ""
    good_reads_desc = give_clean_words_list(good_reads_desc)

    wiki_desc = desc_data["Wikipedia Description"][index]
    if type(wiki_desc) is float:
        wiki_desc = ""
    wiki_desc = give_clean_words_list(wiki_desc)

    read_geek_desc = desc_data["Readgeek Description"][index]
    if type(read_geek_desc) is float:
        read_geek_desc = ""
    read_geek_desc = give_clean_words_list(read_geek_desc)

    riffle_desc = desc_data["Riffle Description"][index]
    if type(riffle_desc) is float:
        riffle_desc = ""
    riffle_desc = give_clean_words_list(riffle_desc)

    amazon_desc = desc_data["Amazon Description"][index]
    if type(amazon_desc) is float:
        amazon_desc = ""
    amazon_desc = give_clean_words_list(amazon_desc)

    output_result = [book_id, title, isbn, rating, author, language, pages, publication, pub_date, pub_month, pub_year,
                     genres, img_url, gp_price, gp_url, bnb_price, bnb_url, indie_price, indie_url, amazon_price,
                     amazon_url, r1, r1_url, r2, r2_url, r3, r3_url, r4, r4_url, r5, r5_url, good_reads_desc, wiki_desc,
                     read_geek_desc, riffle_desc, amazon_desc]

    # Reviews File
    no_comments = 0
    while True:
        reviews_index += 1
        try:
            review_isbn = reviews_data["ISBN"][reviews_index]
            review_book_title = reviews_data["Book Title"][reviews_index]

        except KeyError:
            break

        if review_book_title == title or review_isbn == isbn:
            user_id = reviews_data["User ID"][reviews_index]
            user_name = reviews_data["User Name"][reviews_index]
            user_url = reviews_data["User URL"][reviews_index]
            review_date = reviews_data["Review Date"][reviews_index]
            review_text = reviews_data["Review"][reviews_index]
            user_rating = reviews_data["Rating"][reviews_index]
            if type(review_text) is float:
                review_text = ""
            review_text = give_clean_words_list(review_text)
            out_user_review.writerow([book_id, title, isbn, user_id, user_name, user_url, user_rating,
                                      review_date, review_text])
            no_comments += 1
        else:
            reviews_index -= 1
            break
    print("Comments = " + str(no_comments))

    # Genre Classifier

    tokens = good_reads_desc + wiki_desc + read_geek_desc + riffle_desc + amazon_desc + author.split(" ")
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

    try:
        genre_scores = np.array(genre_scores)
        index_scores = np.argsort(genre_scores)
        genre_scores = np.sort(genre_scores)

    except TypeError:
        for genre in genre_list:
            output_result.append(0)
        out.writerow(output_result)
        continue

    base = genre_scores[-4]
    percent_changes = []
    for i in range(0, 3):
        curr = genre_scores[no_of_genres - 1 - i]
        percent_changes.append(((curr - base) / base) * 100)
    percent_changes = np.array(percent_changes)
    base_percent = (100 - percent_changes.sum()) / 4

    genre_dict = dict()
    genre_dict = defaultdict(lambda: 0, genre_dict)
    for i in range(0, 3):
        genre_index = index_scores[no_of_genres - 1 - i]
        genre_name = genre_list[genre_index]
        genre_value = percent_changes[i] + base_percent
        print(genre_name + " " + str(genre_value) + "%")
        genre_dict[genre_name] = genre_value
    genre_dict[genre_list[index_scores[-4]]] = base_percent
    print(genre_list[index_scores[-4]] + " " + str(base_percent) + "%\n")

    for genre in genre_list:
        output_result.append(genre_dict[genre])

    out.writerow(output_result)

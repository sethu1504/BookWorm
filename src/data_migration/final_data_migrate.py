from pymongo import MongoClient
import pandas as pd


def give_text_format(text):
    if len(text) == 0:
        return []
    text = text[1: len(text) - 1]
    new_list = []
    for word in text.split(","):
        new_list.append(word.replace("'", '').strip())
    return new_list

mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
mongo_brie_db = mongo_client.Brie

books_collection = mongo_brie_db.Books

books_data = pd.read_csv("../../data/final_1_combined.csv")

for index, row in books_data.iterrows():
    book_id = row["ID"]
    title = row["Book Title"]
    print(str(index) + " " + title)
    isbn = row["ISBN"]
    rating = row["Rating"]

    author = row["Author"]
    if type(author) is float:
        author = ""

    language = row["Language"]
    if type(language) is float:
        language = ""

    pages = row["Pages"]

    publication = row["Publication"]
    if type(publication) is float:
        publication = ""

    pub_date = row["Publish Date"]
    pub_month = row["Publish Month"]
    pub_year = row["Publish Year"]

    genres = row["Genres"]
    if type(genres) is float:
        genres = ""

    image = row["Image"]
    if type(image) is float:
        image = ""

    gp_price = float(row["Google Play"])
    gp_url = row["Google Play URL"]
    if type(gp_url) is float:
        gp_url = ""

    bnb_price = float(row["Barnes and Noble"])
    bnb_url = row["Barnes and Noble URL"]
    if type(bnb_url) is float:
        bnb_url = ""

    indie_price = float(row["Indie Bound"])
    indie_url = row["Indie Bound URL"]
    if type(indie_url) is float:
        indie_url = ""

    try:
        amazon_price = float(row["Amazon"])
    except ValueError:
        amazon_price = -1
    amazon_url = row["Amazon URL"]
    if type(amazon_url) is float:
        amazon_url = ""

    r1 = row["R1"]
    if type(r1) is float:
        r1 = ""

    r2 = row["R2"]
    if type(r2) is float:
        r2 = ""

    r3 = row["R3"]
    if type(r3) is float:
        r3 = ""

    r4 = row["R4"]
    if type(r4) is float:
        r4 = ""

    r5 = row["R5"]
    if type(r1) is float:
        r5 = ""

    r1_url = row["R1 URL"]
    if type(r1_url) is float:
        r1_url = ""

    r2_url = row["R2 URL"]
    if type(r2_url) is float:
        r2_url = ""

    r3_url = row["R3 URL"]
    if type(r3_url) is float:
        r3_url = ""

    r4_url = row["R4 URL"]
    if type(r4_url) is float:
        r4_url = ""

    r5_url = row["R5 URL"]
    if type(r5_url) is float:
        r5_url = ""

    good_reads_desc = row["GoodReads_Description"]
    if type(good_reads_desc) is float:
        good_reads_desc = ""

    wiki_desc = row["Wiki_Description"]
    if type(wiki_desc) is float:
        wiki_desc = ""

    read_geek_desc = row["Readgeek_Description"]
    if type(read_geek_desc) is float:
        read_geek_desc = ""

    riffle_desc = row["Riffle_Description"]
    if type(riffle_desc) is float:
        riffle_desc = ""

    amazon_desc = row["Amazon_Description"]
    if type(amazon_desc) is float:
        amazon_desc = ""

    genre_list = ["crime", "fantasy", "young-adult", "romance", "comedy", "dystopia", "action", "historical",
                  "non-fiction", "science fiction", "self-help"]

    genre_dict = dict()
    for genre in genre_list:
        genre_score = row[genre]
        if genre_score != 0:
            genre_dict[genre] = genre_score

    doc = dict()
    doc["id"] = book_id
    doc["title"] = title
    doc["isbn"] = isbn
    doc["rating"] = rating
    doc["author"] = author
    doc["pages"] = int(pages)
    doc["language"] = language
    doc["publication"] = publication
    doc["pub_date"] = pub_date
    doc["pub_month"] = pub_month
    doc["pub_year"] = pub_year
    doc["genres"] = give_text_format(genres)
    doc["image"] = image
    doc["google_play_price"] = gp_price
    doc["google_play_url"] = gp_url
    doc["barnes_and_noble_price"] = bnb_price
    doc["barnes_and_noble_url"] = bnb_url
    doc["indie_price"] = indie_price
    doc["indie_url"] = indie_url
    doc["amazon_price"] = amazon_price
    doc["amazon_url"] = amazon_url
    doc["r1"] = r1
    doc["r1_url"] = r1_url
    doc["r2"] = r2
    doc["r2_url"] = r2_url
    doc["r3"] = r3
    doc["r3_url"] = r3_url
    doc["r4"] = r4
    doc["r4_url"] = r4_url
    doc["r5"] = r5
    doc["r5_url"] = r5_url
    doc["goodreads_desc"] = give_text_format(good_reads_desc)
    doc["wiki_desc"] = give_text_format(wiki_desc)
    doc["riffle_desc"] = give_text_format(riffle_desc)
    doc["amazon_desc"] = give_text_format(amazon_desc)
    doc["readgeek_desc"] = give_text_format(read_geek_desc)
    doc["genre_dissect"] = genre_dict

    books_collection.insert_one(doc)



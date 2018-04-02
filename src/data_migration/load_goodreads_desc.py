from pymongo import MongoClient
import pandas as pd

mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
mongo_brie_db = mongo_client.Brie

books_collection = mongo_brie_db.Books_GoodReads

for i in range(1, 6):
    data = pd.read_csv("../../data/batch_" + str(i) + "/description.csv")
    idx = (i * 100000) - 1
    print(idx)
    for index, row in data.iterrows():
        idx += 1
        doc = dict()
        doc["id"] = idx
        doc["title"] = row["Book Title"]
        desc = row["GoodReads Description"]
        if type(desc) is float:
            desc = ""
        doc["goodreads_desc"] = desc
        books_collection.insert_one(doc)


from pymongo import MongoClient
import pandas as pd

mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
mongo_brie_db = mongo_client.Brie

books_similar_collection = mongo_brie_db.Books_Similar

sim_books_data = pd.read_csv("../../data/sim_books_combined.csv")

for index, row in sim_books_data.iterrows():
    print(index)
    doc = dict()
    doc["Id"] = int(row["ID"])
    doc["SIM1"] = int(row["SIM1"])
    doc["SIM2"] = int(row["SIM2"])
    doc["SIM3"] = int(row["SIM3"])
    doc["SIM4"] = int(row["SIM4"])
    doc["SIM5"] = int(row["SIM5"])
    doc["SIM6"] = int(row["SIM6"])
    doc["SIM7"] = int(row["SIM7"])
    doc["SIM8"] = int(row["SIM8"])
    doc["SIM9"] = int(row["SIM9"])
    doc["SIM10"] = int(row["SIM10"])

    books_similar_collection.insert_one(doc)

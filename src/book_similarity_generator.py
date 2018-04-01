import pandas as pd
import csv
import codecs

books_data = pd.read_csv("../data/final_1_combined.csv")
out = csv.writer(codecs.open("../data/sim_books_1.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out.writerow(["ID", "SIM1", "SIM2", "SIM3", "SIM4", "SIM5", "SIM6", "SIM7", "SIM8", "SIM9", "SIM10"])

for index, row in books_data.iterrows():
    if index < 4961:
        continue
    print(str(index) + " " + row["Book Title"])
    author = row["Author"]
    if type(author) is float:
        curr_author = ""
    pub = row["Publication"]
    if type(pub) is float:
        pub = ""
    input_book_tokens = row["Book Title"].split(" ") + author.split(" ") + pub.split(" ") + \
                        row["Wiki_Description"][1:len(row["Wiki_Description"]) - 1].split(",") + \
                        row["Riffle_Description"][1:len(row["Riffle_Description"]) - 1].split(",") + \
                        row["GoodReads_Description"][1:len(row["GoodReads_Description"]) - 1].split(",") + \
                        row["Readgeek_Description"][1:len(row["Readgeek_Description"]) - 1].split(",") + \
                        row["Amazon_Description"][1:len(row["Amazon_Description"])-1].split(",")
    jaccard_sim_dict = dict()
    book_language_dict = dict()
    book_title_dict = dict()
    for index_1, row_1 in books_data.iterrows():
        if row_1["ID"] == row["ID"]:
            continue
        curr_author = row_1["Author"]
        if type(curr_author) is float:
            curr_author = ""
        curr_pub = row_1["Publication"]
        if type(curr_pub) is float:
            curr_pub = ""
        curr_book_tokens = row_1["Book Title"].split(" ") + curr_author.split(" ") + curr_pub.split(" ") + \
                           row_1["Wiki_Description"][1:len(row["Wiki_Description"]) - 1].split(",") + \
                           row_1["Riffle_Description"][1:len(row["Riffle_Description"]) - 1].split(",") + \
                           row_1["GoodReads_Description"][1:len(row["GoodReads_Description"]) - 1].split(",") + \
                           row_1["Readgeek_Description"][1:len(row["Readgeek_Description"]) - 1].split(",") + \
                           row_1["Amazon_Description"][1:len(row["Amazon_Description"])-1].split(",")

        intersection = len(list(set(input_book_tokens).intersection(curr_book_tokens)))
        union = (len(input_book_tokens) + len(curr_book_tokens)) - intersection
        if union == 0:
            jacc_sim = 0
        else:
            jacc_sim = intersection / union
        jaccard_sim_dict[row_1["ID"]] = jacc_sim
        book_language_dict[row_1["ID"]] = row_1["Language"]
        book_title_dict[row_1["ID"]] = row_1["Book Title"]

    i = 1
    write_row = [row["ID"]]
    processed_books = []
    for w in sorted(jaccard_sim_dict, key=jaccard_sim_dict.get, reverse=True):
        curr_title = book_title_dict[w]
        if (curr_title == row["Book Title"]) or (curr_title in processed_books):
            continue
        if row["Language"] == "English":
            if row["Language"] != book_language_dict[w]:
                continue
        write_row.append(w)
        processed_books.append(book_title_dict[w])
        i += 1
        if i == 11:
            break
    print(processed_books)
    out.writerow(write_row)

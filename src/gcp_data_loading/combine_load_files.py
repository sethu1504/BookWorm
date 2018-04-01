import csv
import codecs
import re

#google play, b&n, indie bound, amazon


if __name__ == '__main__':

    print("Working on final_1.csv...")

    remove_words = set(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                    'sold', 'story', 'novel', 'book', 'bestseller', 'bestselling', 'author', 'description',
                    'copies', 'copy', 'publish', 'publisher', 'series', 'release', 'read', 'collection',
                    'cover', 'edition', 'million', 'edition', 'version', 'volume', 'sell'])

    #final_1

    out_all = csv.writer(codecs.open("../../data/final_1_combined.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)

    out_all.writerow(["ID", "Book Title", "ISBN", "Rating", "Author", "Language", "Pages", "Publication", "Publish Date",
                  "Publish Month", "Publish Year", "Genres", "Image", "Google Play", "Google Play URL", "Barnes and Noble",
                  "Barnes and Noble URL", "Indie Bound", "Indie Bound URL",
                  "Amazon", "Amazon URL", "R1", "R1 URL", "R2", "R2 URL", "R3", "R3 URL", "R4", "R4 URL", "R5", "R5 URL",
                  "GoodReads_Description", "Wiki_Description", "Readgeek_Description", "Riffle_Description",
                  "Amazon_Description", "crime", "fantasy", "young-adult", "romance", "comedy", "dystopia", "action",
                  "historical", "non-fiction", "science fiction", "self-help"])

    for i in range(5):
        input_file = open('../../data/batch_'+str(i+1)+'/final_1.csv')
        reader = csv.reader(input_file)
        next(reader, None)
        for row in reader:
            ctr1 = 31
            for j in range(5):
                temp_cell = row[ctr1]
                if temp_cell == "":
                    temp_cell = []
                else:
                    temp_cell = eval(temp_cell)
                    temp_cell = set(temp_cell) - remove_words
                row[ctr1] = list(temp_cell)
                ctr1 += 1

            ctr2 = 13
            for j in range(4):
                temp_price = row[ctr2]
                temp_price = temp_price.strip()
                if ("free" in temp_price.lower()):
                    temp_price = 0
                elif(temp_price.startswith('$')):
                    temp_price = temp_price[1:]
                elif (temp_price is None or temp_price == "" or temp_price == float('nan') or str(temp_price).isspace()):
                    temp_price = -1
                elif "EUR" in temp_price:
                    temp_price = temp_price.replace(",", ".")
                    temp_p=""
                    for char in temp_price:
                        if char.isdigit() or char in ".":
                            temp_p += char
                    temp_price = temp_p
                else:
                    temp_price = -1
                row[ctr2] = temp_price
                ctr2 += 2

            out_all.writerow(row)

    print("Finished.\nWorking on final_2.csv...")

    #final_2
    out_user_review = csv.writer(codecs.open("../../data/final_2_combined.csv", "w", "utf-8"), delimiter=",",
                            quoting=csv.QUOTE_ALL)

    out_user_review.writerow(["ID", "Book Title", "ISBN", "User ID", "User Name", "User URL", "Rating",
                              "Review Data", "Review"])

    for i in range(5):
        input_file = open('../../data/batch_' + str(i+1) + '/final_2.csv')
        reader = csv.reader(input_file)
        # skip header
        next(reader, None)
        for item in reader:
            out_user_review.writerow(item)
    print("Process finished.")

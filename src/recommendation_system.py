from collections import defaultdict

from pymongo import MongoClient
import math

mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
mongo_brie_db = mongo_client.Brie
description_collection = mongo_brie_db.book_secondary_details

# like_books = ["Harry Potter and the Goblet of Fire (Harry Potter, #4)",
#               "The Hunger Games (The Hunger Games, #1)",
#               "Catching Fire (The Hunger Games, #2)",
#               "Storm Born (Dark Swan #1)",
#               "The Shadow of the Wind (The Cemetery of Forgotten Books,  #1)",
#               "Shatter Me (Shatter Me, #1)",
#               "Vampire Academy (Vampire Academy #1)",
#               "The Time Traveler's Wife",
#               "The Da Vinci Code (Robert Langdon, #2)",
#               "Hush, Hush (Hush, Hush, #1)",
#               "City of Bones (The Mortal Instruments, #1)",
#               "The Princess Diaries (The Princess Diaries, #1)",
#               "City of Ashes (The Mortal Instruments, #2)",
#               "Size 12 Is Not Fat (Heather Wells, #1)"]
#
# perm_like_books = list(like_books)
#
# dislike_books = ["Eclipse (Twilight, #3)",
#                  "Twilight (Twilight, #1)",
#                  "Fallen (Fallen, #1)",
#                  "The Historian",
#                  "The Scar (Bas-Lag, #2)",
#                  "The Girl Who Kicked the Hornet's Nest (Millennium, #3)"]
#
# perm_dislike_books = list(dislike_books)


like_books = ["The Redbreast (Harry Hole, #3)",
              "The Cruelest Month (Chief Inspector Armand Gamache, #3)",
              "The Shadow of the Wind (The Cemetery of Forgotten Books,  #1)",
              "The Time Traveler's Wife",
              "The Da Vinci Code (Robert Langdon, #2)",
              "The Historian",
              "The Scar (Bas-Lag, #2)",
              "The Girl Who Kicked the Hornet's Nest (Millennium, #3)",
              "All Mortal Flesh (The Rev. Clare Fergusson & Russ Van Alstyne Mysteries #5)",
              "The Girl with the Dragon Tattoo (Millennium, #1)",
              "Angels & Demons  (Robert Langdon, #1)"
              ]

like_rating = [7, 8, 7, 9, 10, 7, 6, 8, 9, 8, 8]

perm_like_books = list(like_books)

dislike_books = ["Eclipse (Twilight, #3)",
                 "Vampire Academy (Vampire Academy #1)",
                 "Twilight (Twilight, #1)",
                 "Hush, Hush (Hush, Hush, #1)",
                 "Fallen (Fallen, #1)",
                 "Size 12 Is Not Fat (Heather Wells, #1)",
                 "Catching Fire (The Hunger Games, #2)",
                 "Storm Born (Dark Swan #1)",
                 ]
# dislike_books = []

perm_dislike_books = list(dislike_books)

# Generate User Profile
genre_score_dict = dict()
genre_score_dict = defaultdict(lambda: 0, genre_score_dict)

# Dicts to store word probabilities of like and dislike books
like_words_dict = dict()
dislike_words_dict = dict()

like_words_dict = defaultdict(lambda: 0, like_words_dict)
dislike_words_dict = defaultdict(lambda: 0, dislike_words_dict)

like_sim_books = []
# for book in like_books:
#     print(book)
#     similar_books = get_similar_books(book)
#     print(similar_books)
#     for sim_book in similar_books:
#         if (sim_book not in like_books) and (sim_book not in dislike_books) and (sim_book not in like_sim_books):
#             like_sim_books.append(sim_book)

dislike_sim_books = []
# for book in dislike_books:
#     print(book)
#     similar_books = get_similar_books(book)
#     print(similar_books)
#     for sim_book in similar_books:
#         if (sim_book not in like_books) and (sim_book not in dislike_books)and (sim_book not in like_sim_books) and (sim_book not in dislike_sim_books):
#             dislike_sim_books.append(sim_book)

for book in like_books:
    book_second_details = description_collection.find_one({"title": book})
    book_genre_dissect = book_second_details["genre_dissect"]
    for genre in book_genre_dissect:
        genre_score_dict[genre] += book_genre_dissect[genre]

like_books = like_books + like_sim_books
dislike_books = dislike_books + dislike_sim_books

i = 0
for book in like_books:
    desc_words = book_second_details["goodreads"] + book_second_details["wikipedia"] + book_second_details["readgeek"] \
        + book_second_details["riffle"]

    review_list = book_second_details["reviews"]
    for review_dict in review_list:
        review_str_list = review_dict["review"]
        desc_words + review_str_list

    for word in desc_words:
        like_words_dict[word] += like_rating[i]
    i += 1


for book in dislike_books:
    book_second_details = description_collection.find_one({"title": book})
    book_genre_dissect = book_second_details["genre_dissect"]

    desc_words = book_second_details["goodreads"] + book_second_details["wikipedia"] + book_second_details["readgeek"] \
        + book_second_details["riffle"]

    review_list = book_second_details["reviews"]
    for review_dict in review_list:
        review_str_list = review_dict["review"]
        desc_words + review_str_list

    for word in desc_words:
        dislike_words_dict[word] += 1


print(genre_score_dict)
sorted_genre_list = []
for w in sorted(genre_score_dict, key=genre_score_dict.get, reverse=True):
    sorted_genre_list.append(w)

print(sorted_genre_list)

total_words_like = sum(like_words_dict.values())
total_words_dislike = sum(dislike_words_dict.values())

all_words = list(like_words_dict.keys()) + list(dislike_words_dict.keys())
total_unique_words = len(set(all_words))

alpha = 1

book_suggestion_score_dict = dict()
book_suggestion_score_dict = defaultdict(lambda: 0, book_suggestion_score_dict)

word_strength_dict = dict()
word_strength_dict = defaultdict(lambda: 0, word_strength_dict)

basic_genre = sorted_genre_list[0]
secondary_genre = sorted_genre_list[1]
supplementary_genre = sorted_genre_list[2:]

for i in range(0, len(supplementary_genre)):
    supp_genre_1 = supplementary_genre[i]
    for j in range(i+1, len(supplementary_genre)):
        supp_genre_2 = supplementary_genre[j]
        prediction_books = description_collection.find(
            {"$and": [{"genre_dissect." + basic_genre: {"$exists": "true"}},
                      {"genre_dissect." + secondary_genre: {"$exists": "true"}},
                      {"genre_dissect." + supp_genre_1: {"$exists": "true"}},
                      {"genre_dissect." + supp_genre_2: {"$exists": "true"}}]
             })
        print(prediction_books.count())

        for book in prediction_books:
            book_genres = book["genre_dissect"]
            # if not(book_genres[basic_genre]) > book_genres[secondary_genre] > book_genres[supp_genre_1] > \
            #         book_genres[supp_genre_2]:
            #     continue
            desc_words = book["goodreads"] + book["wikipedia"] + book["readgeek"] + book["riffle"]

            like_prob = 0
            dislike_prob = 0
            for word in desc_words:
                word_like_prob = (like_words_dict[word] + alpha) / (total_words_like + total_unique_words)
                word_dislike_prob = (dislike_words_dict[word] + alpha) / (total_words_like + total_unique_words)
                word_strength_dict[word] = math.log(word_like_prob / word_dislike_prob)
                like_prob += math.log(word_like_prob)
                dislike_prob += math.log(word_dislike_prob)
            book_score = like_prob / dislike_prob

            prev_score = book_suggestion_score_dict[book["title"]]
            if book_score > prev_score:
                book_suggestion_score_dict[book["title"]] = book_score

# for w in sorted(word_strength_dict, key=word_strength_dict.get, reverse=True):
#     print(w + " " + str(word_strength_dict[w]))


for w in sorted(book_suggestion_score_dict, key=book_suggestion_score_dict.get, reverse=True):
    if (w in perm_like_books) or (w in perm_dislike_books):
        continue
    print(w + " " + str(book_suggestion_score_dict[w]))

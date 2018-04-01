from django.http import HttpResponse
from django.shortcuts import render
import json
import re
from pymongo import MongoClient
from collections import defaultdict
import math

mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
mongo_brie_db = mongo_client.Brie

books_collection = mongo_brie_db.Books


def index(request):
    return render(request, 'app/index.html')


def search_book(request):
    return render(request, 'app/explore.html')


def search_result(request):
    if request.method == "POST":
        query = (request.POST["query"]).lower()
        rgx = re.compile('.*' + query + '.*', re.IGNORECASE)

        results = books_collection.find({"title": rgx})
        response = []
        print(results)
        for book in results:
            book_dict = dict()
            book_dict["title"] = book["title"]
            book_dict["author"] = book["author"]
            book_dict["publication"] = book["publication"]
            book_dict["img_url"] = book["image"]
            book_dict["id"] = book["id"]
            response.append(book_dict)

        return HttpResponse(json.dumps(response))
    else:
        return HttpResponse('Invalid Request!!')


def book_view(request, book_id):
    book = books_collection.find_one({"id": book_id})

    context = dict()
    context["title"] = book["title"]
    context["author"] = book["author"]
    context["pages"] = book["pages"]
    context["ID"] = book_id
    context["publication"] = book["publication"]
    return render(request, 'app/book_view.html', context)


def overview(request):
    return render(request, 'app/overview.html')


def publishers(request):
    return render(request, 'app/publishers.html')


def recommendation(request):
    return render(request, 'app/recommendation.html')


def authors(request):
    return render(request, 'app/authors.html')


def evaluation(request):
    return render(request, 'app/evaluation.html')


def get_recommendations(request):
    sel_books = request.POST["books"]
    sel_books = json.loads(sel_books)

    like_books_dict = dict()
    dislike_books = []
    like_books = []

    # Create liked and disliked books
    for book in sel_books:
        book_rating = int(book["rating"])
        book_id = int(book["book_id"])
        if book_rating > 5:
            like_books_dict[book_id] = book_rating
            like_books.append(book_id)
        else:
            dislike_books.append(book_id)

    # Fetch Like and dislike books data
    like_books_data = books_collection.find({"id": {"$in": like_books}})
    dislike_books_data = books_collection.find({"id": {"$in": dislike_books}})

    # Generate genre profile
    genre_score_dict = dict()
    genre_score_dict = defaultdict(lambda: 0, genre_score_dict)

    print(like_books)
    for book in like_books_data:
        genre_dissect = book["genre_dissect"]
        for genre in genre_dissect:
            genre_score_dict[genre] += genre_dissect[genre]

    # Take word counts for likes and dislike books
    like_words_dict = dict()
    like_words_dict = defaultdict(lambda: 0, like_words_dict)

    for book in like_books_data:
        tokens = book["goodreads_desc"] + book["riffle_desc"] + book["amazon_desc"] + book["readgeek_desc"] \
                 + book["wiki_desc"] + book["title"].split(" ") + book["publication"].split(" ") \
                 + book["author"].split(" ")
        for word in tokens:
            like_words_dict[word] += like_books_dict[book["id"]]

    dislike_words_dict = dict()
    dislike_words_dict = defaultdict(lambda: 0, dislike_words_dict)

    for book in dislike_books_data:
        tokens = book["goodreads_desc"] + book["riffle_desc"] + book["amazon_desc"] + book["readgeek_desc"] \
                 + book["wiki_desc"] + book["title"].split(" ") + book["publication"].split(" ") \
                 + book["author"].split(" ")
        for word in tokens:
            dislike_words_dict[word] += 1

    # Values needed for probability calculation
    total_words_like = sum(like_words_dict.values())
    total_words_dislike = sum(dislike_words_dict.values())

    all_words = list(like_words_dict.keys()) + list(dislike_words_dict.keys())
    total_unique_words = len(set(all_words))
    alpha = 1

    # Sort genres based on score
    sorted_genre_list = []
    for w in sorted(genre_score_dict, key=genre_score_dict.get, reverse=True):
        sorted_genre_list.append(w)

    print(sorted_genre_list)

    # Dicts for word scores and book recommendation scores
    book_suggestion_score_dict = dict()
    book_suggestion_score_dict = defaultdict(lambda: 0, book_suggestion_score_dict)

    word_strength_dict = dict()
    word_strength_dict = defaultdict(lambda: 0, word_strength_dict)

    # Separate genres
    basic_genre = sorted_genre_list[0]
    secondary_genre = sorted_genre_list[1]
    supplementary_genre = sorted_genre_list[2:]

    # Query and calculate scores for relevant books
    for i in range(0, len(supplementary_genre)):
        supp_genre_1 = supplementary_genre[i]
        for j in range(i + 1, len(supplementary_genre)):
            supp_genre_2 = supplementary_genre[j]
            prediction_books = books_collection.find(
                {"$and": [{"genre_dissect." + basic_genre: {"$exists": "true"}},
                          {"genre_dissect." + secondary_genre: {"$exists": "true"}},
                          {"genre_dissect." + supp_genre_1: {"$exists": "true"}},
                          {"genre_dissect." + supp_genre_2: {"$exists": "true"}}]
                 })

            for book in prediction_books:
                book_genres = book["genre_dissect"]
                # if not(book_genres[basic_genre]) > book_genres[secondary_genre] > book_genres[supp_genre_1] > \
                #         book_genres[supp_genre_2]:
                #     continue
                tokens = book["goodreads_desc"] + book["riffle_desc"] + book["amazon_desc"] + book["readgeek_desc"] \
                    + book["wiki_desc"] + book["title"].split(" ") + book["publication"].split(" ") \
                    + book["author"].split(" ")

                like_prob = 0
                dislike_prob = 0
                for word in tokens:
                    word_like_prob = (like_words_dict[word] + alpha) / (total_words_like + total_unique_words)
                    word_dislike_prob = (dislike_words_dict[word] + alpha) / (total_words_dislike + total_unique_words)
                    word_strength_dict[word] = math.log(word_like_prob / word_dislike_prob)
                    like_prob += math.log(word_like_prob)
                    dislike_prob += math.log(word_dislike_prob)
                book_score = like_prob / dislike_prob

                prev_score = book_suggestion_score_dict[book["title"]]
                if book_score > prev_score:
                    book_suggestion_score_dict[book["title"]] = book_score

    # Results Obtained
    i = 0
    for w in sorted(book_suggestion_score_dict, key=book_suggestion_score_dict.get, reverse=True):
        if (w in like_books) or (w in dislike_books):
            continue
        i += 1
        print(w + " " + str(book_suggestion_score_dict[w]))
        if i == 10:
            break

    return render(request, 'app/recomm_results.html')

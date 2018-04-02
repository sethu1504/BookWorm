from django.http import HttpResponse
from django.shortcuts import render
import json
import re
from pymongo import MongoClient
from collections import defaultdict
import math
import plotly
import plotly.graph_objs as go
import plotly.offline as opy
from plotly.graph_objs import Layout, Bar, Scatter
import numpy as np

mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
mongo_brie_db = mongo_client.Brie

books_collection = mongo_brie_db.Books
similar_books_collection = mongo_brie_db.Books_Similar


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

    # context = dict()
    # context["title"] = book["title"]
    # context["author"] = book["author"]
    # context["pages"] = book["pages"]
    # context["ID"] = book_id
    # context["publication"] = book["publication"]
    # return render(request, 'app/book_view.html', context)

    book = books_collection.find_one({"id": book_id})
    context = dict()
    context["title"] = book["title"]
    context["author"] = book["author"]
    context["pages"] = book["pages"]
    context["ID"] = book_id
    context["publication"] = book["publication"]
    genres_dict = book["genre_dissect"]
    genres_lst = []
    genres_percent = []
    for key, value in genres_dict.items():
        genres_lst.append(key.title())
        genres_percent.append(value)

    colors = ['#ff598f', '#fd8a5e', '#e0e300', '#01dddd']
    trace = go.Pie(labels=genres_lst, values=genres_percent,
                   marker=dict(colors=colors))  # marker=dict(colors=colors, line=dict(color='#000000', width=1)
    data = go.Data([trace])
    layout = go.Layout(title="B.R.I.E's Genre Dissection", height=500, width=500,
                       autosize=False)
    figure = go.Figure(data=data, layout=layout)
    div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False}, show_link=False)
    context["chart"] = div
    return render(request, 'app/book_view.html', context)


def overview(request):
    return render(request, 'app/overview.html')


def publishers(request):

    # Top Publishers by number of books
    publishers_by_books = books_collection.aggregate([{"$group": {"_id": "$publication", "count": {"$sum": 1}}},
                                                      {"$sort": {"count": -1}}, {"$limit": 16}])

    publisher_names = []
    book_count = []
    for pub_book_agg in publishers_by_books:
        pub_name = pub_book_agg["_id"]
        if pub_name == "":
            continue
        publisher_names.append(pub_name)
        book_count.append(pub_book_agg["count"])

    context = dict()

    pub_by_book_div = plotly.offline.plot({"data": [Bar(x=publisher_names, y=book_count,
                                                        marker=dict(color='rgb(135,195,132)'))],
                                           'layout': Layout(title='<b>Top Publishers by Books</b>',
                                                            yaxis=dict(title='Number of Books'))},
                                          output_type="div", include_plotlyjs=False, link_text="", show_link="False")
    context["pub_by_book_div"] = pub_by_book_div

    # Top Publishers by years
    start_year = 1850
    end_year = start_year + 10
    i = 0
    year_labels = []
    publisher_names_by_year = []
    while end_year <= 2020:
        publisher_by_books_by_year = books_collection.aggregate([{"$match": {"pub_year": {"$gte": start_year,
                                                                                          "$lt": end_year}}},
                                                                 {"$group": {"_id": "$publication",
                                                                             "count": {"$sum": 1}}},
                                                                 {"$sort": {"count": -1}}, {"$limit": 2}])

        for publisher in publisher_by_books_by_year:
            if publisher["_id"] == '':
                continue
            year_labels.append(str(start_year) + " - " + str(end_year))
            publisher_names_by_year.append(publisher["_id"])
            i += 1
            break
        end_year += 10
        start_year += 10

    trace = go.Table(
        header=dict(values=[['Decades'], ['Top Publishers']],
                    line=dict(color='black'),
                    fill=dict(color='#a1c3d1')
                    ),
        cells=dict(values=[year_labels,
                           publisher_names_by_year],
                   line=dict(color='black'))
    )

    data = [trace]
    layout = go.Layout(title="<b>Popular Publishers by Decade</b>", height=550, width=600,
                       autosize=False)
    figure = go.Figure(data=data, layout=layout)
    pub_by_year_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
                               show_link=False)

    context["pub_by_year_div"] = pub_by_year_div

    # Price of Books by Publishers
    websites = ["amazon_price", "barnes_and_noble_price", "indie_price", "google_play_price"]
    website_price_dict = dict()
    for website in websites:
        results = books_collection.aggregate([{"$match": {"$and": [{website: {"$gt": 0, "$lte": 100}},
                                                         {"publication": {"$in": publisher_names[0:5]}}]}},
                                             {"$group": {"_id": "$publication", "avgPrice": {"$avg": "$" + website}}}])

        price_list_for_publishers = []
        for row in results:
            price_list_for_publishers.append(row["avgPrice"])

        website_price_dict[website] = price_list_for_publishers

    book_count_np = np.array(book_count)
    book_count_np = book_count_np/10

    trace1 = Scatter(
        x=publisher_names,
        y=website_price_dict["amazon_price"],
        name='Amazon Price'
    )
    trace2 = Bar(
        x=publisher_names,
        y=book_count_np[0:5],
        name='Number of Books in 10s'
    )
    trace3 = Scatter(
        x=publisher_names,
        y=website_price_dict["indie_price"],
        name='Indie Bound Price'
    )
    trace4 = Scatter(
        x=publisher_names,
        y=website_price_dict["barnes_and_noble_price"],
        name='Barnes and Nobel Price'
    )
    trace5 = Scatter(
        x=publisher_names,
        y=website_price_dict["google_play_price"],
        name='Google Play Price'
    )

    mix_layout = Layout(title='<b>Books by Average Price for Publishers</b>')

    mix_data = [trace1, trace2, trace3, trace4, trace5]
    mig_fig = {'data': mix_data, 'layout': mix_layout}
    mix_div = plotly.offline.plot(mig_fig, output_type="div", include_plotlyjs=False, link_text="", show_link="False")

    context["books_by_avg_price_pub_div"] = mix_div

    # Publication by average pages
    publishers_by_pages = books_collection.aggregate([{"$match": {"pages": {"$gt": 0}}},
                                                      {"$group": {"_id": "$publication", "count": {"$sum": 1},
                                                                  "avgPages": {"$avg": "$pages"}}},
                                                      {"$sort": {"avgPages": -1}}])

    pages = []
    pub_pages = []

    idx = 0
    for row in publishers_by_pages:
        if row["count"] <= 20 or row["_id"] == "":
            continue
        idx += 1
        pages.append(row["avgPages"])
        pub_pages.append(row["_id"])
        if idx == 11:
            break

    pub_by_pages_div = plotly.offline.plot({"data": [Bar(x=pub_pages, y=pages,
                                                         marker=dict(color='rgb(0,153,153)'))],
                                            'layout': Layout(title='<b>Publishers by Average No.of Pages</b>',
                                                             yaxis=dict(title='Number of Pages'))},
                                           output_type="div", include_plotlyjs=False, link_text="", show_link="False")
    context["pub_by_pages_div"] = pub_by_pages_div

    # Average Rating by Publisher
    publish_ratings = books_collection.aggregate([{"$match": {"publication": {"$in": publisher_names}}},
                                                  {"$group": {"_id": "$publication", "count": {"$sum": 1},
                                                              "avgRating": {"$avg": "$rating"}}},
                                                  {"$sort": {"avgRating": -1}}])
    ratings_for_publisher = []
    for row in publish_ratings:
        rating = "%.2f" % row["avgRating"]
        ratings_for_publisher.append(rating)

    trace = go.Table(
        header=dict(values=[['Publisher'], ['Average Rating']],
                    line=dict(color='black'),
                    fill=dict(color='#ff80ff')
                    ),
        cells=dict(values=[publisher_names,
                           ratings_for_publisher],
                   line=dict(color='black'))
    )

    data = [trace]
    layout = go.Layout(title="<b>Average Rating of Popular Publishers</b>", height=550, width=600,
                       autosize=False)
    figure = go.Figure(data=data, layout=layout)
    pub_by_rating_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
                                 show_link=False)

    context["pub_by_rating_div"] = pub_by_rating_div

    # Publishers to Authors

    results = books_collection.aggregate([{"$group": {"_id": {"publication": '$publication'},
                                           "authors": {"$addToSet": '$author'}}}, {"$unwind": "$authors"},
                                           {"$group": {"_id": "$_id", "authorCount": {"$sum": 1}}},
                                           {"$sort": {"authorCount": -1}}, {"$limit": 11}])

    pub_for_authors = []
    pub_authors_count = []
    pub_book_count = []
    for row in results:
        publication = row["_id"]["publication"]
        if publication == "":
            continue
        pub_for_authors.append(publication)
        pub_authors_count.append(row["authorCount"])
        supp_results = books_collection.aggregate([{"$match": {"publication": publication}},
                                                   {"$group": {"_id": "$publication", "count": {"$sum": 1}}}])

        for res1 in supp_results:
            pub_book_count.append(res1["count"])

    trace1 = Scatter(
        x=pub_for_authors,
        y=pub_book_count,
        name='Books Published'
    )
    trace2 = Bar(
        x=pub_for_authors,
        y=pub_authors_count,
        name='Authors associated',
        marker=dict(color='rgb(163, 163, 117)')
    )

    mix_layout = Layout(title='<b>Books Published and Unique Authors Involved</b>',
                        yaxis=dict(title='Number of Books & Authors'))

    mix_data = [trace1, trace2]
    mig_fig = {'data': mix_data, 'layout': mix_layout}
    mix_div = plotly.offline.plot(mig_fig, output_type="div", include_plotlyjs=False, link_text="", show_link="False")

    context["books_pub_author_div"] = mix_div

    return render(request, 'app/publishers.html', context)


def recommendation(request):
    return render(request, 'app/recommendation.html')


def authors(request):
    return render(request, 'app/authors.html')


def evaluation(request):
    return render(request, 'app/evaluation.html')


def get_recommendations(request):
    sel_books = request.POST["books"]
    sel_books = json.loads(sel_books)

    like_books_rating_dict = dict()
    dislike_books = []
    like_books = []

    like_books_alone = []
    dislike_books_alone = []

    real_genre_dict = dict()
    real_genre_dict = defaultdict(lambda: 0, real_genre_dict)

    # Create liked and disliked books
    for book in sel_books:
        book_rating = int(book["rating"])
        book_id = int(book["book_id"])
        sim_book_ids = similar_books_collection.find({"Id": book_id})
        if book_rating > 5:
            like_books_rating_dict[book_id] = book_rating
            like_books.append(book_id)
            like_books_alone.append(book_id)
            idx = 1
            for sim_book in sim_book_ids:
                sim_book_id = sim_book["SIM" + str(idx)]
                like_books.append(sim_book_id)
                like_books_rating_dict[sim_book_id] = book_rating
                idx += 1
        else:
            idx = 1
            dislike_books.append(book_id)
            dislike_books_alone.append(book_id)
            for sim_book in sim_book_ids:
                dislike_books.append(sim_book["SIM" + str(idx)])
                idx += 1

    # Fetch Like and dislike books data
    like_books_data = books_collection.find({"id": {"$in": like_books}})
    dislike_books_data = books_collection.find({"id": {"$in": dislike_books}})

    # Generate genre profile
    genre_score_dict = dict()
    genre_score_dict = defaultdict(lambda: 0, genre_score_dict)

    for book in like_books_data:
        real_genres = book["genres"]
        for genre in real_genres:
            real_genre_dict[genre] += 1
        genre_dissect = book["genre_dissect"]
        for genre in genre_dissect:
            genre_score_dict[genre] += genre_dissect[genre]
    print(genre_score_dict)

    # Take word counts for likes and dislike books
    like_words_dict = dict()
    like_words_dict = defaultdict(lambda: 0, like_words_dict)

    like_books_data = books_collection.find({"id": {"$in": like_books}})
    for book in like_books_data:
        tokens = book["goodreads_desc"] + book["riffle_desc"] + book["amazon_desc"] + book["readgeek_desc"] \
                 + book["wiki_desc"] + book["title"].split(" ") + book["publication"].split(" ") \
                 + book["author"].split(" ")
        # print(like_books_rating_dict[book["id"]])
        for word in tokens:
            like_words_dict[word] += like_books_rating_dict[book["id"]]

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

    real_sorted_genre_list = []
    del real_genre_dict["Fiction"]
    for w in sorted(real_genre_dict, key=real_genre_dict.get, reverse=True):
        real_sorted_genre_list.append(w)

    has_child = False
    if "Childrens" in real_sorted_genre_list[0:4]:
        has_child = True

    book_suggestion_score_dict = dict()
    book_suggestion_score_dict = defaultdict(lambda: 0, book_suggestion_score_dict)

    word_strength_dict = dict()
    word_strength_dict = defaultdict(lambda: 0, word_strength_dict)

    prediction_books = books_collection.find()
    for book in prediction_books:
        actual_book_genres = book["genres"]
        at_least_one = False
        for genre in real_sorted_genre_list[0:4]:
            if genre in actual_book_genres[0:4]:
                if not has_child and "Childrens" in actual_book_genres[0:4]:
                    continue
                at_least_one = True
                break

        if not at_least_one:
            continue

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

        prev_score = book_suggestion_score_dict[book["id"]]
        if book_score > prev_score:
            book_suggestion_score_dict[book["id"]] = book_score

    # Construct Response
    response = []
    i = 0
    for w in sorted(book_suggestion_score_dict, key=book_suggestion_score_dict.get, reverse=True):
        if (w in like_books_alone) or (w in dislike_books):
            continue
        book_dets = books_collection.find_one({"id": w})
        book_language = book_dets["language"]
        if book_language != "English" or book_language == "":
            continue
        book_name = book_dets["title"]
        i += 1
        print(book_name + " " + str(book_suggestion_score_dict[w]))
        book_dict = dict()
        book_dict["id"] = w
        book_dict["title"] = book_name
        book_dict["author"] = book_dets["author"]
        book_dict["img_url"] = book_dets["image"]
        book_dict["publication"] = book_dets["publication"]
        book_dict["score"] = book_suggestion_score_dict[w]
        response.append(book_dict)
        if i == 30:
            break
    i = 0

    for w in sorted(word_strength_dict, key=word_strength_dict.get, reverse=True):
        print(w + " " + str(word_strength_dict[w]))
        i += 1
        if i == 30:
            break

    return HttpResponse(json.dumps(response))

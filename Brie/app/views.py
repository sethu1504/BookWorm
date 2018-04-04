from django.http import HttpResponse
from django.shortcuts import render
import json
import re
from pymongo import MongoClient
import math
import plotly.graph_objs as go
import plotly.offline as opy
from collections import defaultdict
from collections import Counter
import plotly.plotly
from plotly.graph_objs import Bar, Scatter, Layout
import numpy as np

mongo_client = MongoClient('mongodb://sethu:sethu123@localhost:27017/Brie')
mongo_brie_db = mongo_client.Brie

books_collection = mongo_brie_db.Books
similar_books_collection = mongo_brie_db.Books_Similar
goodreads_description = mongo_brie_db.Books_GoodReads


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
    book_similar = similar_books_collection.find_one({"Id": book_id})
    book_goodreads_desc = goodreads_description.find_one({"id": book_id})

    context = dict()
    context["title"] = book["title"]
    context["author"] = book["author"]
    context["pages"] = book["pages"]
    context["ID"] = book_id
    context["publication"] = book["publication"]
    context["image"] = book["image"]
    context["indie_price"] = book["indie_price"]
    context["indie_url"] = book["indie_url"]

    context["google_play_url"] = book["google_play_url"]
    context["google_play_price"] = book["google_play_price"]

    context["barnes_and_noble_price"] = book["barnes_and_noble_price"]
    context["barnes_and_noble_url"] = book["barnes_and_noble_url"]

    context["amazon_price"] = book["amazon_price"]
    context["amazon_url"] = book["amazon_url"]

    context["goodreads_desc"] = book_goodreads_desc["goodreads_desc"]

    genres_dict = book["genre_dissect"]

    sim_list = []

    for i in range(1, 11):
        similar_book = books_collection.find_one({"id": book_similar["SIM" + str(i)]})
        sim_list.append(similar_book)

    context["similar_books"] = sim_list
    #------Charts-------

    genres_lst = []
    genres_percent = []
    for key, value in genres_dict.items():
        genres_lst.append(key.title())
        genres_percent.append(value)

    colors = ['#ff598f', '#fd8a5e', '#e0e300', '#01dddd']
    trace = go.Pie(labels=genres_lst, values=genres_percent,
                   marker=dict(colors=colors))  # marker=dict(colors=colors, line=dict(color='#000000', width=1)
    data = go.Data([trace])
    layout = go.Layout(title="<b>Genre Dissection</b>", height=500, width=500,
                       autosize=False)
    figure = go.Figure(data=data, layout=layout)
    div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False}, show_link=False)
    context["chart"] = div
    return render(request, 'app/book_view.html', context)


def overview(request):

    context = dict()
    popular_books = books_collection.find()  # {"rating": {"$gte": 3}}
    genre_count = dict()
    genre_count = defaultdict(lambda: dict(), genre_count)

    genres_dict = dict()
    genres_dict = defaultdict(lambda: list(), genres_dict)

    decade_dct = dict()
    decade_dct = defaultdict(lambda: list(), decade_dct)

    overall_genres = list()
    years_lst = [1800, 1870, 1960, 2000, 2010]

    overall_prices = dict()
    overall_prices = defaultdict(lambda: 0, overall_prices)

    chart_labels = ['1800 - 1870', '1870 - 1960', '1960 - 2000', '2000 - 2010', '2010 - 2020']

    chart_labels_dict = dict()
    chart_labels_dict = defaultdict(lambda: list(), chart_labels_dict)

    for i in range(len(chart_labels)):
        chart_labels_dict[years_lst[i]] = chart_labels[i]


    number_of_pages_values = []

    book_languages_dict = dict()
    book_languages_dict = defaultdict(lambda: list(), book_languages_dict)

    all_language_lst = []

    language_count_dict = dict()
    # decade_dct = {}
    # for year in years_lst:
    #     decade_dct[year] = list()

    #months_dct = {}
    #for i in range(12):


    # all books are in their respective decades by the end of this for loop
    for book in popular_books:
        publish_year = book['pub_year']
        if publish_year is None or publish_year == "" or str(publish_year).isspace():
            id = book['id'][0]
            if id == str(1):
                publish_year = 2000
            elif id == str(2):
                publish_year = 2010
            elif id == str(3):
                publish_year = 1960
            elif id == str(4):
                publish_year = 1870
            elif id == str(5):
                publish_year = 1800

        if 1800 <= publish_year < 1870:
            year = 1800
        elif 1870 <= publish_year < 1960:
            year = 1870
        elif 1960 <= publish_year < 2000:
            year = 1960
        elif 2000 <= publish_year < 2010:
            year = 2000
        elif 2010 <= publish_year < 2020:
            year = 2010
        decade_dct[year].append(book)

    #book_count = 0

    for year, book in decade_dct.items():
        book_counter_per_yrange = 0
        pages_counter_per_yrange = 0
        for item in book:

            #genre-related
            if len(item["genres"]) == 0 or item["genres"][0] == "":
                genre_dissect = item["genre_dissect"]
                if (len(genre_dissect)) == 0:
                    continue
                else:
                    gen = sorted(genre_dissect.items(), key=lambda x: x[1], reverse=True)
                    popular_genre = gen[0][0]
            else:
                for good_genre in item["genres"]:
                    # fiction is too generalizing
                    if good_genre.lower() != "fiction":
                        popular_genre = good_genre
                        break
                    else:
                        continue
            genres_dict[year].append(popular_genre)
            overall_genres.append(popular_genre)

            # price-related per genre
            price_sum = 0
            if 1 <= item["google_play_price"] <= 100:
                price_sum += item["google_play_price"]
            if 1 <= item["barnes_and_noble_price"] <= 100:
                price_sum += item["barnes_and_noble_price"]
            if 1 <= item["indie_price"] <= 100:
                price_sum += item["indie_price"]
            if 1 <= item["amazon_price"] <= 100:
                price_sum += item["amazon_price"]
            overall_prices[popular_genre] += price_sum

            # #-pages
            pages_counter_per_yrange += item["pages"]
            book_counter_per_yrange += 1

            # #-books/language
            language = item["language"]
            if language == "":
                language = "Unspecified"
            if(language!="Unspecified"): #removing unspecified
                book_languages_dict[year].append(language)
                all_language_lst.append(language)

        number_of_pages_values.append(round(pages_counter_per_yrange / book_counter_per_yrange, 2))

    # chart-1: popular genre by decade
    for year, genres in genres_dict.items():
        genre_count[year] = dict(Counter(genres))


    chart_values = []
    for (key, val) in genre_count.items():
        v = sorted(val.items(), key=lambda x: x[1], reverse=True)
        genre_count[key] = (v[0][0], '<br>', v[1][0],'<br>', v[2][0])
        genre_count[key] = ''.join(genre_count[key])
        chart_values.append(genre_count[key])

    trace = go.Table(header=dict(values=[['Years'], ['<b>Top 3 Genres per Range</b>']],
                                 line=dict(color='black'),
                                 fill=dict(color='#FE4511')),
                     cells=dict(values=[chart_labels, chart_values],
                                line=dict(color='black')))

    data = [trace]
    layout = go.Layout(title="<b>Top 3 Genres per Year Range</b>", height=800, width=700,
                       autosize=False, font=dict( size=17) )
    figure = go.Figure(data=data, layout=layout)
    genres_by_year_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
                                  show_link=False)

    context["genres_by_year_div"] = genres_by_year_div

    # chart-2: top-most genre among all books that we have
    top_most_genres = dict(Counter(overall_genres))
    top_most_genres_sorted_all = sorted(top_most_genres.items(), key=lambda x: x[1], reverse=True)
    top_most_genres_sorted = top_most_genres_sorted_all[0:10]

    genre_sum = 0
    for genre in top_most_genres_sorted:
        genre_sum += genre[1]

    genre_labels = []
    genre_values = []
    for genre in top_most_genres_sorted:
        genre_labels.append(genre[0])
        temp = genre[1]# / genre_sum #normalization
        genre_values.append(temp)

    # data = [go.Bar(
    #     x=genre_labels,
    #     y=genre_values,
    #     xaxis = dict(title = "Number of Books")
    # )]

    trace = go.Bar(
        x=genre_labels,
        y=genre_values,
        name='Number of Books',
        marker=dict(color='rgb(49,130,189)'))

    data = [trace]
    layout = go.Layout( title="<b>Top-10 Genres in Our Collection</b>", height=550, width=1100,
                       autosize=False, yaxis=dict(title='Number of Books'),
                        xaxis=dict(title='Genres'), font=dict( size=15))

    #layout = go.Layout()
    figure = go.Figure(data=data, layout=layout)
    most_popular_genres_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
                                       show_link=False)
    context["most_popular_genres_div"] = most_popular_genres_div

    # chart-6: Languages of all the books that we have

    # chart-3: price per genre

    top_most_genres_dict = dict(top_most_genres_sorted_all) #has books, number
    price_labels = []
    price_values = []

    overall_prices_sorted = sorted(overall_prices.items(), key=lambda x: x[1], reverse=True)
    for item in overall_prices_sorted:
        count = top_most_genres_dict[item[0]]
        price_labels.append(item[0])
        price_values.append(item[1]/count)

    price_labels = price_labels[0:10]
    price_values = price_values[0:10]

    trace = go.Bar(x=price_labels, y=price_values, hoverinfo='label+percent',
                   marker=dict(
                       color=['#ff598f', '#fd8a5e', '#e0e300', '#01dddd',
                              '#ff598f', '#fd8a5e', '#e0e300', '#01dddd',
                              '#ff598f', '#fd8a5e', '#e0e300', '#01dddd'
                              ]))

    data = go.Data([trace])
    layout = go.Layout(title="<b>Average Book-Price per Genre</b>", height=500, width=1100,
                       autosize=False, font=dict( size=15) , yaxis=dict(title='Price of Books'),
                        xaxis=dict(title='Genres'))
    figure = go.Figure(data=data, layout=layout)
    most_priciest_genres_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
                                        show_link=False)
    context["most_priciest_genres_div"] = most_priciest_genres_div

    # chart-4: wordcloud - popular word by decade


    # chart-5: Average number of pages by year-range

    #trace = go.Bar(x=chart_labels, y=number_of_pages_values, )
                   # marker=dict(
                   #     color=['#ff598f', '#fd8a5e', '#e0e300', '#01dddd', '#00ffc5',
                   #            '#ff598f', '#fd8a5e', '#e0e300', '#01dddd',
                   #            '#ff598f', '#fd8a5e', '#e0e300', '#01dddd'
                   #            ]))

                # yaxis=dict(range=[0, 400]), yaxis=dict(
                #        domain=[0, 400],
                #        nticks = 12

    trace = go.Scatter(
        x=chart_labels,
        y=number_of_pages_values, mode="lines+markers+text", text=number_of_pages_values, textposition = "top",
         connectgaps=True, hoverinfo='label+percent'
    )


    data = go.Data([trace])
    layout = go.Layout(title="Average #Pages per Year Range", height=500, width=1100,
                       autosize=False , font=dict( size=15),
                       yaxis=dict(title='Number of Pages', range=[0, 460]),
                       xaxis=dict(title='Years')
                       )
    figure = go.Figure(data=data, layout=layout)
    avg_pages_per_yrange_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
                                        show_link=False)
    context["avg_pages_per_yrange_div"] = avg_pages_per_yrange_div


    #chart-6: #Books per language

    for year, lang in book_languages_dict.items():
        language_count_dict[year] = dict(Counter(lang))

    print(language_count_dict)

    data = []
    for year, langs in language_count_dict.items():
        temp_dict = dict(sorted(langs.items(), key=lambda x: x[1], reverse=True)[0:5])
        #print("year:", year, "val:", temp_dict)
    #     names = list(temp_dict.keys()) #languages
    #     counts = list(temp_dict.values()) #counts
    #
    #     trace = go.Bar(x= chart_labels, y= counts, name = names)
    #     data.append(trace)
    #
    # layout = go.Layout(barmode='stack')
    #
    # fig = go.Figure(data=data, layout=layout)
    # languages_per_yrange_div = opy.plot(fig, auto_open=False, output_type='div', config={"displayModeBar": False},
    #                                     show_link=False)
    # context["languages_per_yrange_div"] = languages_per_yrange_div


    #language_count_lst_sorted = sorted(top_most_genres.items(), key=lambda x: x[1], reverse=True)
    #print("checktype:",language_count_lst_sorted)

    # for year, lang in language_count_lst_sorted:
    #
    #
    #
    #
    # data = []
    # ctr = 0
    # for i in language_count_lst_sorted:
    #     trace = go.Bar(
    #     x= chart_labels[ctr]
    #     y= i.values()
    #     name='SF Zoo'
    # )
    # trace2 = go.Bar(
    #     x=['giraffes', 'orangutans', 'monkeys'],
    #     y=[12, 18, 29],
    #     name='LA Zoo'
    # )
    #
    # data = [trace1, trace2]
    # layout = go.Layout(
    #     barmode='stack'
    # )
    #
    # fig = go.Figure(data=data, layout=layout)
    # py.iplot(fig, filename='stacked-bar')


    # languages_labels = []
    # language_counts = []
    #
    #
    # book_languages_dict = dict(sorted(book_languages_dict.items(), key=lambda x: x[1], reverse=True)[0:10])
    #
    # for language, bk_count in book_languages_dict.items():
    #     languages_labels.append(language)
    #     language_counts.append(bk_count)
    #
    # trace = go.Bar(x=languages_labels, y=language_counts, hoverinfo='label+percent',
    #                marker=dict(
    #                    color=['#ff598f', '#fd8a5e', '#e0e300', '#01dddd',
    #                           '#ff598f', '#fd8a5e', '#e0e300', '#01dddd',
    #                           '#ff598f', '#fd8a5e', '#e0e300', '#01dddd'
    #                           ]))
    #
    # data = go.Data([trace])
    # layout = go.Layout(title="<b>#Books per Language</b>", height=500, width=500,
    #                    autosize=False)
    # figure = go.Figure(data=data, layout=layout)
    # bk_languages_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
    #                                     show_link=False)
    # context["bk_languages_div"] = bk_languages_div





    #chart-7: Number of books by month


    #chart-8: Pages vs Price of books per year_range


    return render(request, 'app/overview.html', context)




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
    layout = go.Layout(title="<b>Average Book Rating of Popular Publishers</b>", height=550, width=600,
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
    context = dict()

    # Top Publishers by number of books
    authors_by_books = books_collection.aggregate([{"$group": {"_id": "$author", "count": {"$sum": 1}}},
                                                   {"$sort": {"count": -1}}, {"$limit": 16}])

    author_names = []
    book_count = []
    for auth_book_agg in authors_by_books:
        auth_name = auth_book_agg["_id"]
        if auth_name == "":
            continue
        author_names.append(auth_name)
        book_count.append(auth_book_agg["count"])

    authors_by_book_div = plotly.offline.plot({"data": [Bar(x=author_names, y=book_count,
                                                        marker=dict(color='rgb(135,195,132)'))],
                                               'layout': Layout(title='<b>Top Authors by Books</b>',
                                                                yaxis=dict(title='Number of Books'))},
                                              output_type="div", include_plotlyjs=False, link_text="",
                                              show_link="False")

    context["authors_by_book_div"] = authors_by_book_div

    # Top Authors by years
    start_year = 1850
    end_year = start_year + 10
    i = 0
    year_labels = []
    author_names_by_year = []
    while end_year <= 2020:
        author_by_books_by_year = books_collection.aggregate([{"$match": {"pub_year": {"$gte": start_year,
                                                                                       "$lt": end_year}}},
                                                              {"$group": {"_id": "$author",
                                                                          "count": {"$sum": 1}}},
                                                              {"$sort": {"count": -1}}, {"$limit": 2}])

        for author in author_by_books_by_year:
            if author["_id"] == '':
                continue
            year_labels.append(str(start_year) + " - " + str(end_year))
            author_names_by_year.append(author["_id"])
            i += 1
            break
        end_year += 10
        start_year += 10

    trace = go.Table(
        header=dict(values=[['Decades'], ['Top Author']],
                    line=dict(color='black'),
                    fill=dict(color='#a1c3d1')
                    ),
        cells=dict(values=[year_labels,
                           author_names_by_year],
                   line=dict(color='black'))
    )

    data = [trace]
    layout = go.Layout(title="<b>Popular Authors every Decade by Production</b>", height=550, width=600,
                       autosize=False)
    figure = go.Figure(data=data, layout=layout)
    authors_by_year_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
                                   show_link=False)

    context["authors_by_year_div"] = authors_by_year_div

    # Bestselling Authors by Price
    bestsellers_authors = ["J.K. Rowling", "Dan Brown", "Julia Donaldson", "James Patterson", "Jacqueline Wilson",
                           "Terry Pratchett", "John Grisham", "Stephenie Meyer", "Martina Cole"]

    bestsellers_value = np.array([209.72, 89.43, 84.23, 86.53, 81.94, 79.06, 71.11, 57.48, 54.41])
    bestsellers_value = bestsellers_value/100

    websites = ["amazon_price", "barnes_and_noble_price", "indie_price", "google_play_price"]
    website_price_dict = dict()
    for website in websites:
        results = books_collection.aggregate([{"$match": {"$and": [{website: {"$gt": 0, "$lte": 100}},
                                                                   {"author": {"$in": bestsellers_authors}}]}},
                                              {"$group": {"_id": "$author", "avgPrice": {"$avg": "$" + website}}}])

        price_list_for_authors = []
        for row in results:
            price_list_for_authors.append(row["avgPrice"])

        website_price_dict[website] = price_list_for_authors

    auth_book_count = []
    for author in bestsellers_authors:
        supp_results = books_collection.aggregate([{"$match": {"author": author}},
                                                   {"$group": {"_id": "$author", "count": {"$sum": 1}}}])

        for res1 in supp_results:
            auth_book_count.append(res1["count"])

    trace1 = Bar(
        x=bestsellers_authors,
        y=auth_book_count,
        name='Number of Books'
    )
    trace2 = Scatter(
        x=bestsellers_authors,
        y=website_price_dict["amazon_price"],
        name='Amazon Price'
    )
    trace3 = Scatter(
        x=bestsellers_authors,
        y=website_price_dict["indie_price"],
        name='Indie Bound Price'
    )
    trace4 = Scatter(
        x=bestsellers_authors,
        y=website_price_dict["barnes_and_noble_price"],
        name='Barnes and Nobel Price'
    )
    trace5 = Scatter(
        x=bestsellers_authors,
        y=website_price_dict["google_play_price"],
        name='Google Play Price'
    )

    mix_layout = Layout(title='<b>Books by Average Price for Bestselling Authors</b>')

    mix_data = [trace1, trace2, trace3, trace4, trace5]
    mig_fig = {'data': mix_data, 'layout': mix_layout}
    mix_div = plotly.offline.plot(mig_fig, output_type="div", include_plotlyjs=False, link_text="", show_link="False")

    context["books_by_avg_price_auth_div"] = mix_div

    # Average Rating for BestSelling Authors

    author_ratings = books_collection.aggregate([{"$match": {"author": {"$in": bestsellers_authors}}},
                                                 {"$group": {"_id": "$author", "count": {"$sum": 1},
                                                             "avgRating": {"$avg": "$rating"}}}])
    ratings_for_author = []
    for row in author_ratings:
        rating = "%.2f" % row["avgRating"]
        ratings_for_author.append(rating)

    trace1 = Scatter(
        x=bestsellers_authors,
        y=bestsellers_value,
        name='Value in 100 millions'
    )
    trace2 = Bar(
        x=bestsellers_authors,
        y=ratings_for_author,
        name='Average Rating',
        marker=dict(color='rgb(163, 163, 117)')
    )

    mix_layout = Layout(title='<b>Comparison of Bestselling Authors</b>')

    mix_data = [trace1, trace2]
    mig_fig = {'data': mix_data, 'layout': mix_layout}
    mix_div = plotly.offline.plot(mig_fig, output_type="div", include_plotlyjs=False, link_text="", show_link="False")

    context["bestsellers_rating_div"] = mix_div

    # Publishers to Authors

    results = books_collection.aggregate([{"$group": {"_id": {"author": '$author'},
                                                      "publications": {"$addToSet": '$publication'}}},
                                          {"$unwind": "$publications"},
                                          {"$group": {"_id": "$_id", "publicationCount": {"$sum": 1}}},
                                          {"$sort": {"publicationCount": -1}}, {"$limit": 11}])

    auth_for_pub = []
    auth_pub_count = []
    pub_book_count = []
    for row in results:
        author = row["_id"]["author"]
        if author == "":
            continue
        auth_for_pub.append(author)
        auth_pub_count.append(row["publicationCount"])
        supp_results = books_collection.aggregate([{"$match": {"author": author}},
                                                   {"$group": {"_id": "$author", "count": {"$sum": 1}}}])

        for res1 in supp_results:
            pub_book_count.append(res1["count"])

    trace1 = Scatter(
        x=auth_for_pub,
        y=pub_book_count,
        name='Books Published',
        marker=dict(color='rgb(255, 102, 102)')
    )
    trace2 = Bar(
        x=auth_for_pub,
        y=auth_pub_count,
        name='Publications associated',
        marker=dict(color='rgb(117, 117, 163)')
    )

    mix_layout = Layout(title='<b>Books Published and Unique Publications Involved</b>',
                        yaxis=dict(title='Number of Books & Publications'))

    mix_data = [trace1, trace2]
    mig_fig = {'data': mix_data, 'layout': mix_layout}
    mix_div = plotly.offline.plot(mig_fig, output_type="div", include_plotlyjs=False, link_text="", show_link="False")

    context["books_pub_author_div"] = mix_div

    return render(request, 'app/authors.html', context)


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
        sim_book_ids = similar_books_collection.find_one({"Id": book_id})
        if book_rating > 5:
            like_books_rating_dict[book_id] = book_rating
            like_books.append(book_id)
            like_books_alone.append(book_id)
            for i in range(1, 11):
                sim_book_id = sim_book_ids["SIM" + str(i)]
                like_books.append(sim_book_id)
                like_books_rating_dict[sim_book_id] = book_rating
        else:
            dislike_books.append(book_id)
            dislike_books_alone.append(book_id)
            for i in range(1, 11):
                print(sim_book_ids["SIM" + str(i)])
                dislike_books.append(sim_book_ids["SIM" + str(i)])

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
    dislike_series = []

    for book in dislike_books_data:
        tokens = book["goodreads_desc"] + book["riffle_desc"] + book["amazon_desc"] + book["readgeek_desc"] \
                 + book["wiki_desc"] + book["title"].split(" ") + book["publication"].split(" ") \
                 + book["author"].split(" ")
        for word in tokens:
            dislike_words_dict[word] += 1
        book_title = book["title"]
        print(book_title)
        series_name = ""
        if "#" in book_title and "(" in book_title:
            brack_index = book_title.find("(")
            series_number_name = book_title[brack_index+1:len(book_title)-2]
            series_name = series_number_name.split(",")[0]
        if len(series_name) > 0:
            dislike_series.append(series_name)

    print(dislike_series)
    # Values needed for probability calculation
    total_words_like = sum(like_words_dict.values())
    total_words_dislike = sum(dislike_words_dict.values())

    all_words = list(like_words_dict.keys()) + list(dislike_words_dict.keys())
    total_unique_words = len(set(all_words))
    alpha = 1

    # Sort genres based on score
    sorted_genre_list = []
    sorted_genre_score_list = []
    for w in sorted(genre_score_dict, key=genre_score_dict.get, reverse=True):
        sorted_genre_list.append(w)
        sorted_genre_score_list.append(genre_score_dict[w])

    real_sorted_genre_list = []
    real_sorted_genre_scores = []
    if "Fiction" in real_genre_dict:
        del real_genre_dict["Fiction"]
    for w in sorted(real_genre_dict, key=real_genre_dict.get, reverse=True):
        real_sorted_genre_list.append(w)
        real_sorted_genre_scores.append(real_genre_dict[w])

    has_child = False
    if "Childrens" in real_sorted_genre_list[0:4]:
        has_child = True

    book_suggestion_score_dict = dict()
    book_suggestion_score_dict = defaultdict(lambda: 0, book_suggestion_score_dict)

    word_strength_dict = dict()
    word_strength_dict = defaultdict(lambda: 0, word_strength_dict)

    prediction_books = books_collection.find()
    for book in prediction_books:
        book_title = book["title"]
        if "#" in book_title and "(" in book_title:
            brack_index = book_title.find("(")
            series_number_name = book_title[brack_index + 1:len(book_title) - 2]
            series_name = series_number_name.split(",")[0]
            if series_name in dislike_series:
                continue

        if (book_title in like_books_alone) or (book_title in dislike_books):
            continue

        actual_book_genres = book["genres"]
        score_multiplier = 0
        at_least_one = False
        for genre in real_sorted_genre_list[0:4]:
            if genre in actual_book_genres[0:4]:
                if not has_child and "Childrens" in actual_book_genres[0:4]:
                    continue
                score_multiplier += 1

        if score_multiplier == 0:
            continue

        tokens = book["goodreads_desc"] + book["riffle_desc"] + book["amazon_desc"] + book["readgeek_desc"] \
            + book["wiki_desc"] + book["title"].split(" ") + book["publication"].split(" ") \
            + book["author"].split(" ")

        like_prob = 0
        dislike_prob = 0
        for word in tokens:
            word_like_prob = (like_words_dict[word] + alpha) / (total_words_like + total_unique_words)
            word_dislike_prob = (dislike_words_dict[word] + alpha) / (total_words_dislike + total_unique_words)
            word_strength_dict[word] = (math.log(word_like_prob / word_dislike_prob)) * like_words_dict[word]
            like_prob += math.log(word_like_prob)
            dislike_prob += math.log(word_dislike_prob)
        book_score = (like_prob / dislike_prob) * score_multiplier

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

    top_words_list = []
    top_words_score = []
    for w in sorted(word_strength_dict, key=word_strength_dict.get, reverse=True):
        print(w + " " + str(word_strength_dict[w]))
        i += 1
        top_words_list.append(w)
        top_words_score.append("%.2f" % word_strength_dict[w])
        if i == 30:
            break

    charts = dict()
    trace = go.Table(
        header=dict(values=[['Word'], ['Score']],
                    line=dict(color='black'),
                    fill=dict(color='#a1c3d1')
                    ),
        cells=dict(values=[top_words_list,
                           top_words_score],
                   line=dict(color='black'))
    )

    data = [trace]
    layout = go.Layout(title="<b>Influential Words</b>", height=550, width=600,
                       autosize=False)
    figure = go.Figure(data=data, layout=layout)
    words_table_div = opy.plot(figure, auto_open=False, output_type='div', config={"displayModeBar": False},
                               show_link=False)

    trace = go.Pie(labels=real_sorted_genre_list[0:5], values=real_sorted_genre_scores[0:5])
    data = go.Data([trace])
    layout = go.Layout(title="<b>Genre Dissection of you taste</b>", height=500, width=500,
                       autosize=False)
    figure = go.Figure(data=data, layout=layout)
    genre_dissect_div = opy.plot(figure, auto_open=False, output_type='div',
                                 config={"displayModeBar": False}, show_link=False)

    charts["genre_dissect"] = genre_dissect_div
    charts["words_table_div"] = words_table_div
    response.append(charts)

    return HttpResponse([json.dumps(response)])

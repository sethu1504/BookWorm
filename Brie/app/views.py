from django.http import HttpResponse
from django.shortcuts import render
import json
import re
from pymongo import MongoClient

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

    return render(request, 'app/recomm_results.html')

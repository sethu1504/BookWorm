from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers

from .models import Book


def index(request):
    return render(request, 'app/index.html')


def list_all(request):
    all_books = Book.objects.all()
    output = ', '.join([b.title for b in all_books])
    context = {'all_books': output}
    return render(request, 'app/list.html', context)


def search_book(request):
    return render(request, 'app/explore.html')


def search_result(request):
    if request.method == "POST":
        query = request.POST["query"]
        data = Book.objects.filter(title__icontains=query)
        data = serializers.serialize('json', data)
        return HttpResponse(data, content_type="application/json")
    else:
        return HttpResponse('Invalid Request!!')


def book_view(request, book_id):
    book = Book.objects.filter(id=book_id)[0]
    context = dict()
    context["title"] = book.title
    context["author"] = book.author
    context["pages"] = book.pages
    context["publication"] = book.publication
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

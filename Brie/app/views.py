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
    print("In here")
    return render(request, 'app/explore.html')


def create(request):
    print("In here")
    if request.method == "POST":
        query = request.POST["query"]
        print("Search = " + query)
        data = Book.objects.filter(title__contains=query)
        print(data)
        data = serializers.serialize('json', data)
        return HttpResponse(data, content_type="application/json")
    else:
        return HttpResponse('Get')

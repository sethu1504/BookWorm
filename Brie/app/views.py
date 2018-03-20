from django.http import HttpResponse
from django.shortcuts import render

from .models import Book


def index(request):
    return render(request, 'app/index.html')


def list_all(request):
    all_books = Book.objects.all()
    output = ', '.join([b.title for b in all_books])
    context = {'all_books': output}
    return render(request, 'app/list.html', context)
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=1000)
    isbn = models.CharField(max_length=200)
    author = models.CharField(max_length=500)
    language = models.CharField(max_length=200)
    publication = models.CharField(max_length=1000)
    pages = models.IntegerField()
    pub_date = models.IntegerField()
    pub_month = models.IntegerField()
    pub_year = models.IntegerField()
    book_url = models.CharField(max_length=500)

    def __str__(self):
        return self.title

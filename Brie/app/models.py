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
    img_url = models.CharField(max_length=500)
    google_price = models.CharField(max_length=100)
    barnes_price = models.CharField(max_length=100)
    indie_price = models.CharField(max_length=100)
    amazon_price = models.CharField(max_length=100, blank=True)
    r1 = models.CharField(max_length=1000, blank=True)
    r2 = models.CharField(max_length=1000, blank=True)
    r3 = models.CharField(max_length=1000, blank=True)
    r4 = models.CharField(max_length=1000, blank=True)
    r5 = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.title

import requests
import lxml.html
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
import csv
import codecs
from url_constants import *
from clean_text import give_clean_words_list

genre_list = ["crime", "fiction"]

number_of_books_per_genre = 100
iterations = int(number_of_books_per_genre / 20)

for genre in genre_list:
    text_file = codecs.open("../data/" + genre + "_words.txt", "w", "utf-8")
    scheme, netloc, path, query_string, fragment = urlsplit(good_reads_explore_genre)
    query_params = parse_qs(query_string)
    query_params["search[query]"] = genre
    new_query_string = urlencode(query_params, doseq=True)
    url = urlunsplit((scheme, netloc, path, new_query_string, fragment))

    for i in range(iterations):
        r = requests.get(url)
        tree = lxml.html.fromstring(r.content)

        books = tree.xpath("//a[@class='bookTitle']")

        for book in books:
            book_url = good_reads_home_url + book.xpath("@href")[0]
            print(book_url)

            book_page_req = requests.get(book_url)
            tree_book = lxml.html.fromstring(book_page_req.content)

            desc_div = tree_book.xpath("//div[@id='description']")
            if len(desc_div) > 0:
                description = desc_div[0].xpath("./span")[-1].text_content().rstrip()

            clean_desc_words = give_clean_words_list(description)

            for word in clean_desc_words:
                text_file.write(word + "\n")

        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)
        query_params["page"] = i + 2
        new_query_string = urlencode(query_params, doseq=True)
        url = urlunsplit((scheme, netloc, path, new_query_string, fragment))
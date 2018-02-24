import requests
import lxml.html
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
import csv
import codecs
from url_constants import *

out = csv.writer(codecs.open("../data/books.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out.writerow(["Book Title", "ISBN", "Description", "Book URL"])

no_of_books_in_each_decade = 200
num_pages = int(no_of_books_in_each_decade / 100)

for i in range(0, len(best_books_url_list)):
    next_url = best_books_url_list[i]
    for j in range(0, num_pages):
        print(next_url)
        r = requests.get(next_url)
        tree = lxml.html.fromstring(r.content)
        books_in_page = tree.xpath("//table[@class='tableList js-dataTooltip']//tr[@itemtype='http://schema.org/Book']")

        for book in books_in_page:
            table_datum = book.xpath("./td")
            details = table_datum[2]
            book_title = details.xpath("./a")[0].xpath("./span")[0].text_content().rstrip()
            book_page_url = good_reads_home_url + details.xpath("./a/@href")[0]
            book_page_req = requests.get(book_page_url)
            tree_book = lxml.html.fromstring(book_page_req.content)
            isbn = tree_book.xpath("//div[@class='infoBoxRowItem']")[1].text_content().rstrip()
            if ":" in isbn:
                index = isbn.find(":")
                isbn = isbn[index+2:len(isbn) - 1]
            desc_div = tree_book.xpath("//div[@id='description']")[0]
            description = desc_div.xpath("./span")[-1].text_content().rstrip()
            out.writerow([book_title, isbn, description, book_page_url])

        scheme, netloc, path, query_string, fragment = urlsplit(next_url)
        query_params = parse_qs(query_string)
        query_params["page"] = str(j+2)
        new_query_string = urlencode(query_params, doseq=True)
        next_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))


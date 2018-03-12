import requests
import lxml.html
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
import csv
import codecs
from url_constants import *


def get_book_details(book_page_url, book_title):
    book_page_req = requests.get(book_page_url)

    tree_book = lxml.html.fromstring(book_page_req.content)
    author = tree_book.xpath("//a[@class='authorName']")[0].xpath("./span")[0].text_content().rstrip()
    pages = tree_book.xpath("//span[@itemprop='numberOfPages']")[0].text_content().rstrip().split(" ")[0]
    publish_details_string = tree_book.xpath("//div[@class='row']")[1].text_content().strip()
    publish_details_list = publish_details_string.split("\n")
    publish_date = publish_details_list[1].strip()
    publication = ""
    if "by" in publish_details_string:
        publication = publish_details_list[2].strip().split("by")[1].strip()

    info_titles = tree_book.xpath("//div[@class='infoBoxRowTitle']")
    det_index = -1
    isbn_index = -1
    lang_index = -1
    for info_title in info_titles:
        det_index += 1
        title = info_title.text_content().rstrip()
        if title == "ISBN" or title == "ISBN13":
            isbn_index = det_index
        elif title == "Edition Language":
            lang_index = det_index
    if isbn_index == -1:
        isbn = -1
    else:
        isbn = tree_book.xpath("//div[@class='infoBoxRowItem']")[isbn_index].text_content().rstrip()
        if ":" in isbn:
            index = isbn.find(":")
            isbn = isbn[index + 2:len(isbn) - 1]

    language = ""
    if lang_index >= 0:
        language = tree_book.xpath("//div[@class='infoBoxRowItem']")[lang_index].text_content().rstrip()

    amazon_url = ""
    amazon_buy_button = tree_book.xpath("//a[@id='buyButton']")
    if len(amazon_buy_button) > 0:
        amazon_url = good_reads_home_url + amazon_buy_button[0].xpath("@href")[0].strip()

    genre_list = []
    genre_divs = tree_book.xpath("//a[@class='actionLinkLite bookPageGenreLink']")
    for genre in genre_divs:
        genre_list.append(genre.text_content().strip())

    desc_div = tree_book.xpath("//div[@id='description']")[0]
    description = desc_div.xpath("./span")[-1].text_content().rstrip()

    return [book_title, isbn, author, language, pages, publication, publish_date, genre_list, book_page_url], \
           [book_title, isbn, amazon_url, description]


def scrape_book_details(isbn, book_title):
    goodreads_id = requests.get(good_reads_isbn_to_id + isbn).text
    book_url = good_reads_home_url + "/book/show/" + goodreads_id

    out = csv.writer(codecs.open("../data/books.csv", "a", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
    out_desc = csv.writer(codecs.open("../data/description.csv", "a", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
    out.writerow(["Book Title", "ISBN", "Author", "Language", "Pages", "Publication", "Publish Date",
                  "Genres", "Book URL"])
    out_desc.writerow(["Book Title", "ISBN", "GoodReads Description", "Amazon URL"])

    book_details = get_book_details(book_url, book_title)

    out.writerow(book_details[0])
    out_desc.writerow(book_details[1])


def scrape_best_books_goodreads():
    out = csv.writer(codecs.open("../data/books.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
    out_desc = csv.writer(codecs.open("../data/description.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
    out.writerow(["Book Title", "ISBN", "Author", "Language", "Pages", "Publication", "Publish Date",
                  "Genres", "Book URL"])
    out_desc.writerow(["Book Title", "ISBN", "Amazon URL", "GoodReads Description"])

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
                print(book_title)
                book_page_url = good_reads_home_url + details.xpath("./a/@href")[0]

                book_details = get_book_details(book_page_url, book_title)

                out.writerow(book_details[0])
                out_desc.writerow(book_details[1])

            scheme, netloc, path, query_string, fragment = urlsplit(next_url)
            query_params = parse_qs(query_string)
            query_params["page"] = str(j+2)
            new_query_string = urlencode(query_params, doseq=True)
            next_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))


if __name__ == '__main__':
    # scrape_book_details("9780545010221", "Example")
    scrape_best_books_goodreads()

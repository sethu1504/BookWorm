import requests
import lxml.html
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
import csv
import codecs
from url_constants import *


def get_user_and_review_stack(tree):
    book_reviews = tree.xpath("//div[@id='bookReviews']")[0]

    user_stack = book_reviews.xpath("//div[@class='reviewHeader uitext stacked']")
    all_reviews = book_reviews.xpath("//div[@class='reviewText stacked']")

    return user_stack, all_reviews


def get_book_details(book_page_url, book_title, rev_out):
    book_page_req = requests.get(book_page_url)

    tree_book = lxml.html.fromstring(book_page_req.content)
    author = tree_book.xpath("//a[@class='authorName']")
    if len(author) > 0:
        author = author[0].xpath("./span")[0].text_content().rstrip()
    pages = tree_book.xpath("//span[@itemprop='numberOfPages']")
    if len(pages) > 0:
        pages = pages[0].text_content().rstrip().split(" ")[0]

    publish_date = ""
    publication = ""
    publish_details_string = tree_book.xpath("//div[@class='row']")
    if len(publish_details_string) > 1:
        publish_details_string = publish_details_string[1].text_content().strip()
        publish_details_list = publish_details_string.split("\n")
        publish_date = publish_details_list[1].strip()
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

    desc_div = tree_book.xpath("//div[@id='description']")
    description = ""
    if len(desc_div) > 0:
        desc_div = desc_div[0]
        description = desc_div.xpath("./span")[-1].text_content().rstrip()

    rating = tree_book.xpath("//span[@class='average']")
    if len(rating) > 0:
        rating = rating[0].text.strip()

    all_users_ratings, all_reviews_stack = get_user_and_review_stack(tree_book)
    for user_rating, review_stack in zip(all_users_ratings, all_reviews_stack):
        review = review_stack.xpath("./span")[0].xpath("./span")[-1].text_content().rstrip()
        review_date = user_rating.xpath("./a")[0].text_content().rstrip()

        user_spans = user_rating.xpath("./span")

        user_url = user_spans[0].xpath("./a/@href")[0]
        user_id = user_url.split("/")[-1].split("-")[0]
        abs_user_url = good_reads_home_url + user_url
        user_name = user_spans[0].xpath("./a")[0].text_content().rstrip()

        rating = -1
        if len(user_spans) > 1:
            stars = user_spans[1].xpath("./span")
            rating = 0
            for star in stars:
                star_class = star.get("class")
                if star_class == "staticStar p10":
                    rating += 1
                else:
                    break
        rev_out.writerow([book_title, isbn, user_id, user_name, abs_user_url, review, review_date, rating])

    return [book_title, isbn, rating, author, language, pages, publication, publish_date, genre_list, book_page_url], \
           [book_title, isbn, amazon_url, description]


def scrape_book_details(isbn, book_title):
    goodreads_id = requests.get(good_reads_isbn_to_id + isbn).text
    book_url = good_reads_home_url + "/book/show/" + goodreads_id

    out = csv.writer(codecs.open("../data/books.csv", "a", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
    out_desc = csv.writer(codecs.open("../data/description.csv", "a", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
    out.writerow(["Book Title", "ISBN", "Rating", "Author", "Language", "Pages", "Publication", "Publish Date",
                  "Genres", "Book URL"])
    out_desc.writerow(["Book Title", "ISBN", "GoodReads Description", "Amazon URL"])

    book_details = get_book_details(book_url, book_title)

    out.writerow(book_details[0])
    out_desc.writerow(book_details[1])


def scrape_best_books_goodreads():
    out = csv.writer(codecs.open("../data/batch_2/books.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
    out_desc = csv.writer(codecs.open("../data/batch_2/description.csv", "w", "utf-8"), delimiter=",",
                          quoting=csv.QUOTE_ALL)
    out_review = csv.writer(codecs.open("../data/batch_2/reviews_users.csv", "w", "utf-8"), delimiter=",",
                            quoting=csv.QUOTE_ALL)
    out.writerow(["Book Title", "ISBN", "Rating", "Author", "Language", "Pages", "Publication", "Publish Date",
                  "Genres", "Book URL"])
    out_desc.writerow(["Book Title", "ISBN", "Amazon URL", "GoodReads Description"])
    out_review.writerow(["Book Title", "ISBN", "User ID", "User Name", "User URL", "Review", "Review Date", "Rating"])

    for i in range(0, len(best_books_url_list)):
        book_id = 1
        next_url = best_books_url_list[i]
        r = requests.get(next_url)
        tree = lxml.html.fromstring(r.content)
        num_pages = int(tree.xpath("//div[@class='pagination']")[0].xpath("./a")[-2].text_content().strip())
        for j in range(1, num_pages + 1):
            print(next_url)
            r = requests.get(next_url)
            tree = lxml.html.fromstring(r.content)
            books_in_page = tree.xpath("//table[@class='tableList js-dataTooltip']//tr[@itemtype='http://schema.org/Book']")

            for book in books_in_page:
                table_datum = book.xpath("./td")
                details = table_datum[2]
                book_title = details.xpath("./a")[0].xpath("./span")[0].text_content().rstrip()
                print(str(book_id) + " " + book_title)
                book_page_url = good_reads_home_url + details.xpath("./a/@href")[0]

                book_details = get_book_details(book_page_url, book_title, out_review)

                out.writerow(book_details[0])
                out_desc.writerow(book_details[1])
                book_id += 1

            scheme, netloc, path, query_string, fragment = urlsplit(next_url)
            query_params = parse_qs(query_string)
            query_params["page"] = str(j+1)
            new_query_string = urlencode(query_params, doseq=True)
            next_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))


if __name__ == '__main__':
    # scrape_book_details("9780545010221", "Example")
    scrape_best_books_goodreads()

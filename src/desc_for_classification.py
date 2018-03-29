import requests
import lxml.html
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
import codecs
from url_constants import *
from clean_text import give_clean_words_list

genre_list = ["crime", "fiction", "fantasy", "young-adult", "romance", "comedy", "dystopia",
              "action", "historical", "non-fiction", "science fiction", "self-help"]


number_of_books_per_genre = 500
iterations = int(number_of_books_per_genre / 20)

for genre in genre_list:
    print(genre)
    text_file = codecs.open("../data/word_bags/" + genre + "_words.txt", "w", "utf-8")
    scheme, netloc, path, query_string, fragment = urlsplit(good_reads_explore_genre)
    query_params = parse_qs(query_string)
    if '+' in genre or '-' in genre:
        query_params['q'] = genre
    else:
        query_params["search[query]"] = genre
    new_query_string = urlencode(query_params, doseq=True)
    url = urlunsplit((scheme, netloc, path, new_query_string, fragment))
    print(url)

    for i in range(iterations):
        print(i)
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

            author = tree_book.xpath("//a[@class='authorName']")
            if len(author) > 0:
                author = author[0].xpath("./span")[0].text_content().rstrip()

            clean_desc_words = give_clean_words_list(description)
            clean_desc_words = clean_desc_words + author.split(" ")

            for word in clean_desc_words:
                text_file.write(word + "\n")

        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)
        query_params["page"] = i + 2
        new_query_string = urlencode(query_params, doseq=True)
        url = urlunsplit((scheme, netloc, path, new_query_string, fragment))
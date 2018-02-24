from url_constants import *

import lxml.html
import pandas as pd
import time
import csv
import codecs

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def get_user_and_review_stack(br):
    content = br.page_source
    tree = lxml.html.fromstring(content)

    book_reviews = tree.xpath("//div[@id='bookReviews']")[0]

    user_stack = book_reviews.xpath("//div[@class='reviewHeader uitext stacked']")
    all_reviews = book_reviews.xpath("//div[@class='reviewText stacked']")

    return user_stack, all_reviews


books_data = pd.read_csv("../data/books.csv")
browser = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')

out = csv.writer(codecs.open("../data/reviews_users.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out.writerow(["ISBN", "User ID", "User Name", "User URL", "Review", "Review Date"])

for index, row in books_data.iterrows():
    print(row["Book Title"])
    isbn = row["ISBN"]
    browser.get(row["Book URL"])
    time.sleep(3)

    isNextPage = True

    while isNextPage:
        all_users_ratings, all_reviews_stack = get_user_and_review_stack(browser)
        for user_rating, review_stack in zip(all_users_ratings, all_reviews_stack):
            review = review_stack.xpath("./span")[0].xpath("./span")[-1].text_content().rstrip()
            review_date = user_rating.xpath("./a")[0].text_content().rstrip()

            user_spans = user_rating.xpath("./span")

            user_url = user_spans[0].xpath("./a/@href")[0]
            user_id = user_url.split("/")[-1].split("-")[0]
            abs_user_url = good_reads_home_url + user_url
            user_name = user_spans[0].xpath("./a")[0].text_content().rstrip()
            print(user_name)

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
            out.writerow([isbn, user_id, user_name, abs_user_url, review, review_date])
        try:
            next_elem = browser.find_element_by_class_name("next_page")
            next_page_class = next_elem.get_attribute("class")
            if next_page_class == "next_page disabled":
                isNextPage = False
            else:
                next_elem.click()
                time.sleep(3)
        except NoSuchElementException:
            isNextPage = False



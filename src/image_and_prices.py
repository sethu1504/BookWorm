import pandas as pd
import requests
import lxml.html
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
import csv
import codecs
import numpy as np

def get_price_google_play(google_play_url):
    google_play = requests.get(google_play_url)
    tree = lxml.html.fromstring(google_play.content)
    time.sleep(2)

    google_play_price_path = tree.xpath(
        '//*[@id="body-content"]/div/div/div[1]/div/div[1]/div/div[2]/div[1]/div/div[3]/span/span/span[2]/button/span/text()')
    google_play_price = ''.join(google_play_price_path)

    if google_play_price == '':
        return 'NaN'
    else:
        return google_play_price


def get_price_barnes_and_noble(barnes_and_noble_url):
    barnes_and_noble_book = requests.get(barnes_and_noble_url)
    tree = lxml.html.fromstring(barnes_and_noble_book.content)
    time.sleep(2)

    barnes_and_noble_path = tree.xpath('//*[@id="pdp-cur-price"]/text()')
    barnes_and_noble_price = ''.join(barnes_and_noble_path)

    if barnes_and_noble_price == '':
        return 'NaN'
    else:
        return '$'+barnes_and_noble_price


def get_price_indie_bound(indie_bound_url):
    indie_bound_book = requests.get(indie_bound_url)
    tree = lxml.html.fromstring(indie_bound_book.content)
    time.sleep(2)

    indie_bound_path = tree.xpath('//*[@id="list-price-price"]/text()')
    str_price = ''.join(indie_bound_path)

    indie_bound_price = str_price.replace('*', '')

    if indie_bound_price == '':
        return 'NaN'
    else:
        return '$'+indie_bound_price

# To log in to Riffle Books to search books using their ISBN to fetch data

browser = webdriver.Firefox(executable_path='/home/ldua/geckodriver')
riffle_sign_in_url = 'https://www.rifflebooks.com/users/sign_in'
browser.get(riffle_sign_in_url)

riffle_login = browser.find_element_by_xpath('//*[@id="href_auth_me"]').click()

time.sleep(3)
input_email_ID = browser.find_element_by_xpath('//*[@id="user_email"]')
input_email_ID.send_keys('lakshaydua22@gmail.com')
input_email_ID.send_keys(Keys.TAB)

time.sleep(3)
input_password = browser.find_element_by_xpath('//*[@id="user_password"]')
input_password.send_keys('Helloworld123')
input_password.send_keys(Keys.ENTER)
time.sleep(3)

# Now we are logged into Riffle.
# We can start scrapping using ISBN.

# df = pd.read_csv('../data/description.csv')
# df['Riffle Description'] = ""

v = open('../data/description.csv')
r = csv.reader(v)
# row0 = next(r)
# row0.append('Riffle Description')
out_description = csv.writer(codecs.open("../data/description_goodreads_riffle", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out_description.writerow(['Book Title','ISBN','Amazon URL','GoodReads Description','Wikipedia Description','Readgeek Description','Riffle Description'])

# df_prices = pd.DataFrame(columns=['Book Title','ISBN','Book Image','Google Play','Barnes and Noble','Indie Bound'])

out_prices = csv.writer(codecs.open("../data/image_and_prices.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out_prices.writerow(['Book Title','ISBN','Book Image','Google Play','Barnes and Noble','Indie Bound'])
# ["Book Title","ISBN","Book Image","Google Play","Barnes and Noble","Indie Bound"]


# To get book URLs from Riffle search results
# We enter ISBN in search bar and select the first suggestion

riffle_book_url = "rifflebooks.com"

# for index, row in df.iterrows():
for item in r:
    ISBN = item[0]
    title = item[1]

    input_search_ISNB = browser.find_element_by_xpath('//*[@id="navSearchField"]')
    input_search_ISNB.send_keys(ISBN)
    input_search_ISNB.send_keys(Keys.ENTER)
    time.sleep(2)

    #select_result = browser.find_element_by_xpath('//*[@id="navSearchField"]')
    input_search_ISNB.send_keys(Keys.DOWN)
    input_search_ISNB.send_keys(Keys.ENTER)
    input_search_ISNB.clear()
    time.sleep(2)

    if browser.current_url == riffle_book_url:
        price_google, price_barnes, price_indie, book_image_url = 'NaN','NaN','NaN','NaN'
        # df_prices = df_prices.append(
        #     {'Book Title': title, 'ISBN': ISBN, 'Book Image': book_image_url,
        #      'Google Play': price_google, 'Barnes and Noble': price_barnes, 'Indie Bound': price_indie},
        #     ignore_index=True)
        out_prices.writerow([title,ISBN,book_image_url,price_google,price_barnes,price_indie])
        continue

    else:
        riffle_book_url = browser.current_url


    riffle_book = requests.get(riffle_book_url)
    tree = lxml.html.fromstring(riffle_book.content)

    google_play = tree.xpath('//div[@id="menuBuy"]/ul/li/a[contains(text(), "Google Play")]/@href')
    google_play_url = ''.join(google_play)

    barnes_and_noble = tree.xpath('//div[@id="menuBuy"]/ul/li/a[contains(text(), "Barnes & Noble")]/@href')
    barnes_and_noble_url = ''.join(barnes_and_noble)

    indie_bound = tree.xpath('//div[@id="menuBuy"]/ul/li/a[contains(text(), "IndieBound")]/@href')
    indie_bound_url = ''.join(indie_bound)

    book_image = tree.xpath('/html/body/div[4]/div[2]/div[1]/div[1]/img/@src')
    book_image_url = ''.join(book_image)

    riffle_book_descr = tree.xpath('/html/body/div[4]/div[2]/div[1]/div[3]/h4/text()')
    riffle_book_description = ''.join(riffle_book_descr).strip()

    # df.set_value(index, 'Riffle Description', riffle_book_description)
    # df.at[index, 'Riffle Description'] = riffle_book_description

    try:
        price_google = get_price_google_play(google_play_url)
    except:
        price_google = 'NaN'
        print("Price not found on Google Play Books")

    try:
        price_barnes = get_price_barnes_and_noble(barnes_and_noble_url)
    except:
        price_barnes = 'NaN'
        print("Price not found on Barnes and Noble")

    try:
        price_indie = get_price_indie_bound(indie_bound_url)
    except:
        price_indie = 'NaN'
        print("Price not found on Indie Bound")

    print(ISBN)
    print(google_play_url)
    print(barnes_and_noble_url)
    print(indie_bound_url)
    print(riffle_book_description)
    print(price_google, price_barnes, price_indie)

    # df_prices = df_prices.append({'Book Title': title, 'ISBN': ISBN, 'Book Image': book_image_url, 'Google Play': price_google, 'Barnes and Noble': price_barnes, 'Indie Bound': price_indie}, ignore_index=True)
    out_prices.writerow([title, ISBN, book_image_url, price_google, price_barnes, price_indie])
    item.append(riffle_book_description)
    out_description.writerow(item)
# df.to_csv('../data/description_goodreads_riffle.csv')

# df_prices.to_csv('../data/image_and_prices.csv')

# df_prices contains Book Title, ISBN, Book Image, Google Play, Barnes and Noble, Indie Bound



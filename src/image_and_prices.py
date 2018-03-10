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

def get_price_amazon(amazon_url):
    amazon_book = requests.get(amazon_url)
    tree = lxml.html.fromstring(amazon_book.content)
    time.sleep(2)

    price = tree.xpath('//*[@id="buybox"]/div/table/tbody/tr[2]/td[2]/text()')
    if price == []:
        price = tree.xpath('//*[@id="buyNewSection"]/a/h5/div/div[2]/div/span[2]/text()')

    if price == []:
        price = tree.xpath('//*[@id="buyNewSection"]/h5/div/div[2]/div/span[2]/text()')

    if price == []:
        price = tree.xpath('//*[@id="usedBuySection"]/h5/div/div[2]/div/span[2]/text()')

    elif price == []:
        print("Amazon price not found")
        return 'NaN'

    str_price = ''.join(price)

    regex_amazon_price = re.findall('(\$\d+[.]\d+)', str_price)
    amazon_price = ''.join(regex_amazon_price)

    if amazon_price == '':
        return 'NaN'
    else:
        return amazon_price



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

df = pd.read_csv('../data/books.csv')
df_prices = pd.DataFrame(columns=['Book Title','ISBN','Book Image','Amazon','Google Play','Barnes and Noble','Indie Bound'])

list_ISBN = list(df.ISBN.values)

# To get book URLs from Riffle search results
# We enter ISBN in search bar and select the first suggestion

riffle_book_url = "rifflebooks.com"

for index, row in df.iterrows():

    ISBN = row['ISBN']
    title = row['Book Title']


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
        price_amazon, price_google, price_barnes, price_indie, book_image_url = 'NaN','NaN','NaN','NaN','NaN'
        df_prices = df_prices.append(
            {'Book Title': title, 'ISBN': ISBN, 'Book Image': book_image_url, 'Amazon': price_amazon,
             'Google Play': price_google, 'Barnes and Noble': price_barnes, 'Indie Bound': price_indie},
            ignore_index=True)
        continue

    else:
        riffle_book_url = browser.current_url


    riffle_book = requests.get(riffle_book_url)
    tree = lxml.html.fromstring(riffle_book.content)

    amazon = tree.xpath('//div[@id="menuBuy"]/ul/li/a[contains(text(), "Amazon")]/@href')
    amazon_url = ''.join(amazon)            # to remove brackets

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

    try:
        price_amazon = get_price_amazon(amazon_url)
    except:
        price_amazon = 'NaN'
        print("Price not found on Amazon")

    try:
        price_google = get_price_google_play(google_play_url)
    except:
        print("Price not found on Google Play Books")

    try:
        price_barnes = get_price_barnes_and_noble(barnes_and_noble_url)
    except:
        print("Price not found on Barnes and Noble")

    try:
        price_indie = get_price_indie_bound(indie_bound_url)
    except:
        print("Price not found on Indie Bound")

    print(ISBN)
    print(amazon_url)
    print(google_play_url)
    print(barnes_and_noble_url)
    print(indie_bound_url)
    print(riffle_book_description)
    print(price_amazon, price_google, price_barnes, price_indie)

    df_prices = df_prices.append({'Book Title': title, 'ISBN': ISBN, 'Book Image': book_image_url, 'Amazon': price_amazon, 'Google Play': price_google, 'Barnes and Noble': price_barnes, 'Indie Bound': price_indie}, ignore_index=True)

df_prices.to_csv('../data/image_and_prices.csv')

# df_prices contains Book Title, ISBN, Book Image, Amazon, Google Play, Barnes and Noble, Indie Bound



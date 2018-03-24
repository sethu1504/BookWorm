import requests
import lxml.html
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
import codecs

def get_price_google_play(google_play_url):
    google_play = requests.get(google_play_url)
    tree = lxml.html.fromstring(google_play.content)

    google_play_price_path = tree.xpath('//*[@id="body-content"]/div/div/div[1]/div/div[1]/div/div[2]/div[1]/div/div[3]/span/span/span[2]/button/span/text()')
    google_play_price = ''.join(google_play_price_path)
    google_play_book_url_path = tree.xpath('//*[@id="body-content"]/div/div/div[1]/div/div[1]/div/div[2]/div[1]/div/div[1]/a/@href')
    google_play_url = ''.join(google_play_book_url_path)

    if google_play_price_path == '':
        google_play_price = 'NaN'

    if google_play_price.count('$') > 1:
        regex = re.findall('(\$[^$]*)$', google_play_price)
        google_play_price = ''.join(regex)

    if google_play_book_url_path == '':
        google_play_url = 'NaN'
    else:
        google_play_url = 'https://play.google.com'+ google_play_url

    return google_play_price, google_play_url


def get_price_barnes_and_noble(barnes_and_noble_url):
    barnes_and_noble_book = requests.get(barnes_and_noble_url)
    tree = lxml.html.fromstring(barnes_and_noble_book.content)
    # time.sleep(2)

    barnes_and_noble_path = tree.xpath('//*[@id="pdp-cur-price"]/text()')
    barnes_and_noble_price = ''.join(barnes_and_noble_path)

    if barnes_and_noble_price == '':
        return 'NaN'
    else:
        return '$'+barnes_and_noble_price


def get_price_indie_bound(indie_bound_url):
    indie_bound_book = requests.get(indie_bound_url)
    tree = lxml.html.fromstring(indie_bound_book.content)
    # time.sleep(2)

    indie_bound_path = tree.xpath('//*[@id="list-price-price"]/text()')
    str_price = ''.join(indie_bound_path)

    indie_bound_price = str_price.replace('*', '')

    if indie_bound_price == '':
        return 'NaN'
    else:
        return '$'+indie_bound_price

def get_price_abebooks(abebooks_url):
    abebooks_book = requests.get(abebooks_url)
    tree = lxml.html.fromstring(abebooks_book.content)

    abebooks_price_path = tree.xpath('//*[@id="book-1"]/div[2]/div[2]/div[1]/span/text()')
    abebooks_price = ''.join(abebooks_price_path)
    abebooks_book_url_path = tree.xpath('//*[@id="book-1"]/div[2]/div[1]/h2/a/@href')
    abebooks_book_url = ''.join(abebooks_book_url_path)

    if abebooks_price != '':
        final_abebooks_price = '$' + abebooks_price[4:]
    else:
        final_abebooks_price = 'NaN'

    if abebooks_book_url != '':
        final_abebooks_book_url = 'https://www.abebooks.com' + abebooks_book_url
    else:
        final_abebooks_book_url = 'NaN'

    return final_abebooks_price, final_abebooks_book_url

# To log in to Riffle Books to search books using their ISBN to fetch data

browser = webdriver.Firefox(executable_path='/home/ldua/geckodriver')
riffle_sign_in_url = 'https://www.rifflebooks.com/users/sign_in'
browser.get(riffle_sign_in_url)

riffle_login = browser.find_element_by_xpath('//*[@id="href_auth_me"]').click()

time.sleep(2)
input_email_ID = browser.find_element_by_xpath('//*[@id="user_email"]')
input_email_ID.send_keys('lakshaydua22@gmail.com')
input_email_ID.send_keys(Keys.TAB)

time.sleep(2)
input_password = browser.find_element_by_xpath('//*[@id="user_password"]')
input_password.send_keys('Helloworld123')
input_password.send_keys(Keys.ENTER)
time.sleep(6)

# Now we are logged into Riffle.
# We can start scrapping using ISBN.

file_description = open('../data/batch_1/description_wikipedia_readgeek.csv')
read_description = csv.reader(file_description)
next(read_description, None)

out_description = csv.writer(codecs.open("../data/batch_1/description_wikipedia_readgeek_riffle.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out_description.writerow(['Book Title','ISBN','Amazon URL','GoodReads Description','Wikipedia Description','Readgeek Description','Riffle Description'])

out_prices = csv.writer(codecs.open("../data/batch_1/image_and_prices.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out_prices.writerow(['Book Title','ISBN','Book Image','Google Play','Google Play URL','Barnes and Noble','Barnes and Noble URL','Indie Bound','Indie Bound URL','Abebooks','Abebooks URL'])

# To get book URLs from Riffle search results
# We enter ISBN in search bar and select the first suggestion

riffle_book_url = "rifflebooks.com"


for row in read_description:
    title = row[0]
    ISBN = row[1]

    if ISBN == '-1':
        book_image_url, price_google, google_play_book_url, price_barnes, barnes_and_noble_url, price_indie, indie_bound_url = 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN'
        out_prices.writerow([title, ISBN, book_image_url, price_google, google_play_book_url, price_barnes, barnes_and_noble_url,price_indie, indie_bound_url])
        continue

    try:
        input_search_ISNB = browser.find_element_by_xpath('//*[@id="navSearchField"]')
        input_search_ISNB.send_keys(ISBN)
        input_search_ISNB.send_keys(Keys.ENTER)
        time.sleep(2)

        # select_result = browser.find_element_by_xpath('//*[@id="navSearchField"]')
        input_search_ISNB.send_keys(Keys.DOWN)
        input_search_ISNB.send_keys(Keys.ENTER)
        input_search_ISNB.clear()
        time.sleep(2)
    except:
        browser.get('https://www.rifflebooks.com/');
        time.sleep(6)
        input_search_ISNB = browser.find_element_by_xpath('//*[@id="navSearchField"]')
        input_search_ISNB.send_keys(ISBN)
        input_search_ISNB.send_keys(Keys.ENTER)
        time.sleep(2)

        # select_result = browser.find_element_by_xpath('//*[@id="navSearchField"]')
        input_search_ISNB.send_keys(Keys.DOWN)
        input_search_ISNB.send_keys(Keys.ENTER)
        input_search_ISNB.clear()
        time.sleep(2)


    if browser.current_url == riffle_book_url:
        book_image_url,price_google,google_play_book_url,price_barnes,barnes_and_noble_url,price_indie,indie_bound_url = 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
        out_prices.writerow([title, ISBN, book_image_url, price_google, google_play_book_url, price_barnes, barnes_and_noble_url,price_indie, indie_bound_url])
        continue

    else:
        riffle_book_url = browser.current_url


    riffle_book = requests.get(riffle_book_url)
    tree = lxml.html.fromstring(riffle_book.content)

    # google_play = tree.xpath('//div[@id="menuBuy"]/ul/li/a[contains(text(), "Google Play")]/@href')
    # google_play_url = ''.join(google_play)

    # barnes_and_noble = tree.xpath('//div[@id="menuBuy"]/ul/li/a[contains(text(), "Barnes & Noble")]/@href')
    # barnes_and_noble_url = ''.join(barnes_and_noble)

    # indie_bound = tree.xpath('//div[@id="menuBuy"]/ul/li/a[contains(text(), "IndieBound")]/@href')
    # indie_bound_url = ''.join(indie_bound)

    book_image = tree.xpath('/html/body/div[4]/div[2]/div[1]/div[1]/img/@src')
    book_image_url = ''.join(book_image)

    riffle_book_descr = tree.xpath('/html/body/div[4]/div[2]/div[1]/div[3]/h4/text()')
    riffle_book_description = ''.join(riffle_book_descr).strip()

    try:
        google_play_url = 'https://play.google.com/store/search?q='+ title +'&c=books'
        price_google, google_play_book_url = get_price_google_play(google_play_url)
    except:
        price_google = 'NaN'
        google_play_book_url ='NaN'
        print("Price not found on Google Play Books")

    try:
        barnes_and_noble_url = 'http://www.barnesandnoble.com/s/?store=allproducts&keyword='+ISBN
        price_barnes = get_price_barnes_and_noble(barnes_and_noble_url)
    except:
        price_barnes = 'NaN'
        barnes_and_noble_url = 'NaN'
        print("Price not found on Barnes and Noble")

    try:
        indie_bound_url = 'http://www.indiebound.org/book/'+ISBN+'?aff=rifflebooks'
        price_indie = get_price_indie_bound(indie_bound_url)
    except:
        price_indie = 'NaN'
        indie_bound_url = 'NaN'
        print("Price not found on Indie Bound")

    try:
        abebooks_url = 'https://www.abebooks.com/book-search/isbn/'+ISBN
        price_abebooks, abebooks_book_url = get_price_abebooks(abebooks_url)

    except:
        price_abebooks = 'NaN'
        abebooks_book_url = 'NaN'
        print("Price not found on Abebooks")

    print(ISBN)
    # print(google_play_url)
    # print(barnes_and_noble_url)
    # print(indie_bound_url)
    # print(riffle_book_description)
    # print(price_google, price_barnes, price_indie)

    out_prices.writerow([title, ISBN, book_image_url, price_google, google_play_book_url, price_barnes, barnes_and_noble_url, price_indie, indie_bound_url, price_abebooks, abebooks_book_url])

    row.append(riffle_book_description)
    out_description.writerow(row)
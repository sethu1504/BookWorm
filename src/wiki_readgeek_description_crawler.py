import requests
import pandas as pd
import lxml.html as lh
from selenium import webdriver
import time
from fuzzywuzzy import fuzz
from url_constants import *


def wiki_description_crawler(book_titles):
    browser = webdriver.Firefox(executable_path='/Users/reet/Libraries/geckodriver')
    browser.get(google_url)
    timeout = 2
    #url_list = []
    wiki_descriptions_list = []
    for i in book_titles:
        # go to Google and simulate browser actions to search for titles of books
        # in case no wikipedia page, wrapping in try and except blocks
        try:
            # remove series content and brackets
            i = i.split("(", 1)[0]
            browser.get(google_url)

            query = 'wikipedia novel ' + i
            inputElement = browser.find_element_by_name('q')
            inputElement.send_keys(query)
            inputElement.submit()
            time.sleep(timeout)

            url = browser.find_element_by_xpath("//div[@class='rc']//a[contains(text(), 'Wikipedia')]") \
                .get_attribute("href")

            if (url is None or url == ""):
                #url_list.append("")
                wiki_descriptions_list.append("")
                continue
            #url_list.append(url)

            # get content from wiki page
            wiki_page = requests.get(url)
            tree = lh.fromstring(wiki_page.content)
            title = tree.xpath('//h1[@id="firstHeading"]//text()')[0]

            #if the wikipedia page is for a movie instead
            if ('film' in title):
                wiki_descriptions_list.append('')
                continue

            match = fuzz.ratio(title, i)
            if (match >= 50):
                description = ''.join(tree.xpath("//div[@class='mw-parser-output']/p[1]//text()"))
            else:
                description = ''
        except:
            description = ''
        wiki_descriptions_list.append(description)
        print(i, title)
    return wiki_descriptions_list


def amazon_description_crawler(amazon_urls):
    pass

def readgeek_description_crawler(isbns):
    geek_descriptions_list = []
    for i in isbns:
        if (i == "-1"):
            geek_descriptions_list.append("")
            continue
        # generate query for readgeek in the format specified
        readgeek_query_url = readgeek_url + i

        # geek_page_url is the first search result
        geek_query_result = requests.get(readgeek_query_url)
        tree1 = lh.fromstring(geek_query_result.content)
        description = ''
        try:
            temp_url = tree1.xpath("//*[@id='searchresults']/div[1]/div[1]/div/a/@href")
            if (temp_url is None):
                geek_descriptions_list.append("")
                continue

            temp_geek_url = tree1.xpath("//*[@id='searchresults']/div[1]/div[1]/div/a/@href")
            if ((temp_geek_url is None) or (not temp_geek_url)):  # if list is empty
                geek_descriptions_list.append("")
                continue

            geek_page_url = 'https://www.readgeek.com' + temp_geek_url[0]
            if (geek_page_url is None or geek_page_url == ""):
                geek_descriptions_list.append("")
                continue

            # geek_page is the actual page of the book. Fetch description from it
            geek_page = requests.get(geek_page_url)
            tree2 = lh.fromstring(geek_page.content)
            description = ''.join(tree2.xpath("//*[@id='blurb']//text()")[1:])
        except:
            description = ''
        print(i)
        geek_descriptions_list.append(description)

    return geek_descriptions_list


# '/Users/reet/PycharmProjects/BookWorm/data/books.csv')
main_desc_df = pd.read_csv('../data/description.csv', encoding='utf-8')
isbn_list = main_desc_df['ISBN'].tolist()
book_titles_list = main_desc_df['Book Title'].tolist()

print("---------Wikipedia---------")
wiki_descrs = wiki_description_crawler(book_titles_list)
print("---------ReadGeek----------")
readgeek_descrs = readgeek_description_crawler(isbn_list)

wiki_df = pd.DataFrame(wiki_descrs, columns=['wikipedia'])
readgeek_df = pd.DataFrame(readgeek_descrs, columns=['readgeek'])

wiki_df = wiki_df.loc[~wiki_df.index.duplicated(keep='first')]
readgeek_df = readgeek_df.loc[~readgeek_df.index.duplicated(keep='first')]

main_desc_df = main_desc_df.loc[~main_desc_df.index.duplicated(keep='first')]
main_desc_df = pd.concat([main_desc_df, wiki_df, readgeek_df], axis=1)

main_desc_df.to_csv('../data/description_readgeek_wikipedia.csv', encoding='utf-8', index=False)
# remove Book, Description, name of the book

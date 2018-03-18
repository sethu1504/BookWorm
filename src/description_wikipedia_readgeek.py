import requests
import pandas as pd
import lxml.html as lh
from selenium import webdriver
import time
from fuzzywuzzy import fuzz
from url_constants import *
import csv
import codecs
import re


def wiki_description_crawler(browser, title, timeout):
    try:
        print(title)
        candidate_description_list = []
        browser.get(google_url)

        wiki_description = ''
        # removing series content and brackets
        title = (title.split("(", 1)[0]).strip()
        browser.get(google_url)

        query = 'wikipedia novel ' + title
        inputElement = browser.find_element_by_name('q')
        inputElement.send_keys(query)
        inputElement.submit()
        time.sleep(timeout)

        urls = browser.find_elements_by_xpath("//div[@class='rc']//a[contains(text(), 'Wikipedia')]")
        #selecting top 2 Wikipedia results

        urls = urls[:2]
        for elem in urls:
            url = elem.get_attribute("href")

            # get the page content from the fetched wikipedia page
            wiki_page = requests.get(url)
            tree = lh.fromstring(wiki_page.content)

            #fetch wikipedia page's title and compare it with the book title
            wikipage_title = " ".join(tree.xpath('//h1[@id="firstHeading"]//text()')) #list is obtained
            wikipage_title = re.sub(' +', ' ', wikipage_title)

            #in case it is a movie, don't consider it
            if ('film' in wikipage_title):
                continue

            #for fuzzymatching giving perfect result, remove keywords (novel) which hampers result
            wikipage_title = (re.sub(r'\(novel\)', '', wikipage_title)).strip()

            #fuzzyword matching. If the titles match more than 50%, consider them
            match = fuzz.ratio(wikipage_title, title)
            if (match >= 50):
                wiki_description = ''.join(tree.xpath("//div[@class='mw-parser-output']/p[1]//text()"))
                candidate_description_list.append((wiki_description, match, url))

        #of the obtained 2, choose the one which matches the most
        if (len(candidate_description_list) > 1):
            #if both match-counts are equal (tied), then the first match is most probable. Choose that
            if(candidate_description_list[0][1]==candidate_description_list[1][1]):
                wiki_description = candidate_description_list[0][0]
            else:
                candidate_description_list = sorted(candidate_description_list, key=lambda x: x[1])
                wiki_description = candidate_description_list[-1][0]
                #print(candidate_description_list[-1][1], candidate_description_list[-1][2])
        else:
            wiki_description = candidate_description_list[0][0]
            #print(candidate_description_list[-1][1], candidate_description_list[-1][2])
        #print(wiki_description)
        return (wiki_description)
    except:
        return ''


def readgeek_description_crawler(isbn):
    try:
        print(isbn)
        if (isbn == '-1'):
            return ''

        # generate query for readgeek in the format specified
        readgeek_query_url = readgeek_url + isbn

        # geek_page_url is the first search result
        geek_query_result = requests.get(readgeek_query_url)
        tree1 = lh.fromstring(geek_query_result.content)

        temp_url = tree1.xpath("//*[@id='searchresults']/div[1]/div[1]/div/a/@href")
        if (temp_url is None):
            return ''

        temp_geek_url = tree1.xpath("//*[@id='searchresults']/div[1]/div[1]/div/a/@href")
        if ((temp_geek_url is None) or (not temp_geek_url)):  # if list is empty
            return ''

        geek_page_url = 'https://www.readgeek.com' + temp_geek_url[0]
        if (geek_page_url is None or geek_page_url == ""):
            return ''

        # geek_page is the actual page of the book. Fetch description from it
        geek_page = requests.get(geek_page_url)
        tree2 = lh.fromstring(geek_page.content)
        geek_description = ''.join(tree2.xpath("//*[@id='blurb']//text()")[1:])
        return geek_description
    except:
        return ''


description_input_file = open('../data/description.csv')
reader = csv.reader(description_input_file)
out_description = csv.writer(codecs.open("../data/description_wikipedia_readgeek.csv", "w", "utf-8"), delimiter=",",
                             quoting=csv.QUOTE_ALL)
out_description.writerow(
    ['Book Title', 'ISBN', 'Amazon URL', 'GoodReads Description', 'Wikipedia Description', 'Readgeek Description'])

# skip header
next(reader, None)
selenium_timeout = 1

# browser is the context to run selenium code for wikipedia
browser = webdriver.Firefox(executable_path='/Users/reet/Libraries/geckodriver')

for item in reader:
    title = item[0]
    isbn = item[1]
    amazon_url = item[2]
    good_descr = item[3]
    wiki_descr = wiki_description_crawler(browser, title, selenium_timeout)
    readgeek_descr = readgeek_description_crawler(isbn)
    out_description.writerow([title, isbn, amazon_url, good_descr, wiki_descr, readgeek_descr])
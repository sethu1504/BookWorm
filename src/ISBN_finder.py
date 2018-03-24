import requests
import lxml.html
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
import codecs

file_description = open('../data/batch_4/description.csv')
read_description = csv.reader(file_description)
next(read_description, None)

out_description = csv.writer(codecs.open("../data/batch_4/description_2.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out_description.writerow(['Book Title','ISBN','Amazon URL','GoodReads Description'])


for row in read_description:
    title = row[0]
    ISBN = row[1]

    if ISBN == '-1':
        print(title)
        try:
            print('try abe')
            search_url = 'https://www.abebooks.com/servlet/SearchResults?sts=t&tn='+title
            search = requests.get(search_url)

            tree = lxml.html.fromstring(search.content)

            book_name = tree.xpath('/html/body/div/div/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/p[2]/span[2]/a/text()')
            scrapped_ISBN = ''.join(book_name)
            print(scrapped_ISBN)
            row[1] = scrapped_ISBN

            if row[1] == '-1' or row[1] == '':
                print('try biblio')
                b_search_url = 'https://www.biblio.com/search.php?stage=1&title=' + title
                b_search = requests.get(b_search_url)

                tree = lxml.html.fromstring(b_search.content)

                book_name = tree.xpath(
                    '/html/body/div[2]/div[2]/div[3]/div/div[1]/div[4]/div[1]/div[1]/div[3]/div[2]/div[1]/ul/li[2]/a[2]/text()')
                scrapped_ISBN = ''.join(book_name)
                print(scrapped_ISBN)
                row[1] = scrapped_ISBN

            if row[1] == '-1' or row[1] == '':
                print('try indie')
                i_search_url = 'https://www.indiebound.org/search/book?keys='+title
                i_search = requests.get(i_search_url)

                tree = lxml.html.fromstring(i_search.content)

                book_name = tree.xpath(
                    '/html/body/div[1]/div/section/div[2]/form/div[2]/div[2]/h2/a/@href')

                scrapped_ISBN = ''.join(book_name)

                print(scrapped_ISBN)
                row[1] = scrapped_ISBN[-13:]

            if row[1] == '-1' or row[1] == '':
                row[1] = '-1'

        except:
            row[1] = '-1'
            print('handled:')

    print('write', row[1])
    out_description.writerow(row)

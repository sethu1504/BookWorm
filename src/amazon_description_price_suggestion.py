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

def get_amazon_price(amazon_url, browser):

    found_price = False

    if not browser:
        browser.get(amazon_url)

    for i in range(10):
        try:
            if browser.find_element_by_xpath('//*[@id="a-autoid-'+ str(i) +'-announce"]/span[1]').text == 'Paperback':
                amazon_price = browser.find_element_by_xpath('//*[@id="a-autoid-'+ str(i) +'-announce"]/span[2]/span').text
                found_price = True
                return amazon_price

        except:
            continue

    if not found_price:
        for i in range(10):
            try:
                if browser.find_element_by_xpath('//*[@id="a-autoid-' + str(i) + '-announce"]/span[1]').text == 'Hardcover':
                    amazon_price = browser.find_element_by_xpath('//*[@id="a-autoid-' + str(i) + '-announce"]/span[2]/span').text
                    found_price = True
                    return amazon_price

            except:
                continue

    if not found_price:
        try:
            price = browser.find_element_by_xpath('//*[@id="newOfferAccordionRow"]/div/div[1]/a/h5/div/div[2]/span[2]').text
            if price == []:
                price = browser.find_element_by_xpath('//*[@id="buybox"]/div/table/tbody/tr[2]/td[2]').text

            if price == []:
                price = browser.find_element_by_xpath('//*[@id="buyNewSection"]/a/h5/div/div[2]/div/span[2]').text

            # if price == []:
            #     price = browser.find_element_by_xpath('//*[@id="buyNewSection"]/h5/div/div[2]/div/span[2]').text

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

        except:
            return 'NaN'

def get_amazon_suggestions(amazon_url, total_suggestions, browser):

    if not browser:
        browser.get(amazon_url)

    suggestion_data =  dict()                       # Dictionary
    number_of_suggestions = total_suggestions +1

    for i in range(1, number_of_suggestions):

        try:
            suggestion_title = browser.find_element_by_xpath('//h2[text()="Customers who bought this item also bought"]/../../../div[2]/div/div[2]/div/ol/li['+str(i)+']/div/a/div[2]').text
            suggestion_url = browser.find_element_by_xpath('//h2[text()="Customers who bought this item also bought"]/../../../div[2]/div/div[2]/div/ol/li['+str(i)+']/div/a').get_attribute("href")

            suggestion_data[suggestion_title] = suggestion_url

        except:
            continue

    return suggestion_data


















def get_amazon_description(amazon_url, selenium_instance):

    # if not selenium_instance:
    #     browser.get(amazon_url)

    browser.switch_to.frame(browser.find_element_by_css_selector("#bookDesc_iframe"))  # To switch to iframe

    desc = browser.find_element_by_xpath('//*[@id="iframeContent"]').text


    print(desc)





































browser = webdriver.Firefox(executable_path='/home/ldua/geckodriver')
df = pd.read_csv('../data/description.csv')

for index, row in df.iterrows():

    # good_reads_amazon_url = 'https://www.amazon.com/gp/product/B073TJBYTB/ref=amb_link_3?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=hero-quick-promo&pf_rd_r=NZMCWJV8Q91PG0F29997&pf_rd_r=NZMCWJV8Q91PG0F29997&pf_rd_t=201&pf_rd_p=1aeb5983-d340-458e-a130-2b54e81d5b71&pf_rd_p=1aeb5983-d340-458e-a130-2b54e81d5b71&pf_rd_i=B019E9WCKI'

    good_reads_amazon_url = row['Amazon URL']

    # To handle amazon.in / amazon.ca / amazon.co.uk / amazon.fr links

    browser.get(good_reads_amazon_url)
    amazon_url = browser.current_url

    if '.com' not in amazon_url:
        if 'amazon.in' in amazon_url:
            amazon_url = amazon_url.replace('amazon.in', 'amazon.com')
            browser.get(amazon_url)

        elif 'amazon.ca' in amazon_url:
            amazon_url = amazon_url.replace('amazon.ca', 'amazon.com')
            browser.get(amazon_url)

        elif 'amazon.co.uk' in amazon_url:
            amazon_url = amazon_url.replace('amazon.co.uk', 'amazon.com')
            browser.get(amazon_url)

        elif 'amazon.fr' in amazon_url:
            amazon_url = amazon_url.replace('amazon.fr', 'amazon.com')
            browser.get(amazon_url)

    # amazon_price = get_amazon_price(amazon_url, True)
    # suggestion_dict = get_amazon_suggestions(amazon_url, 5, True)
    # amazon_description = get_amazon_description(amazon_url, True)






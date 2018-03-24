import requests
import lxml.html
import time
import re
from selenium import webdriver
import csv
import codecs


def get_amazon_price(amazon_url, selenium_instance):

    found_price = False

    if not selenium_instance:
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

def get_amazon_recommendation(amazon_url, number_of_recommendations, selenium_instance):

    if not selenium_instance:
        browser.get(amazon_url)

    recommendation_data =  list()
    total_recommendation = number_of_recommendations + 1

    for i in range(1, total_recommendation):

        try:
            recommendation_title = browser.find_element_by_xpath('//h2[text()="Customers who bought this item also bought"]/../../../div[2]/div/div[2]/div/ol/li['+str(i)+']/div/a/div[2]').text
            recommendation_url = browser.find_element_by_xpath('//h2[text()="Customers who bought this item also bought"]/../../../div[2]/div/div[2]/div/ol/li['+str(i)+']/div/a').get_attribute("href")

            recommendation_data.append(recommendation_title)
            recommendation_data.append(recommendation_url)

        except:
            continue

    return recommendation_data

def get_amazon_description(amazon_url, selenium_instance):

    if not selenium_instance:
        browser.get(amazon_url)

    try:
        browser.switch_to.frame(browser.find_element_by_css_selector("#bookDesc_iframe"))  # To switch to iframe
        amazon_description = browser.find_element_by_xpath('//*[@id="iframeContent"]').text
        return amazon_description

    except:
        return ''

browser = webdriver.Firefox(executable_path='/home/ldua/geckodriver')

# df_description = pd.read_csv('../data/description_wikipedia_readgeek_riffle.csv')
# df_description['Amazon Description'] = ""

file_description = open('../data/batch_1/description_wikipedia_readgeek_riffle.csv')
read_description = csv.reader(file_description)
next(read_description, None)

out_description = csv.writer(codecs.open("../data/batch_1/description_all.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out_description.writerow(['Book Title','ISBN','Amazon URL','GoodReads Description','Wikipedia Description','Readgeek Description','Riffle Description','Amazon Description'])

# df_prices = pd.read_csv('../data/image_and_prices.csv')
# df_prices['Amazon'] = ""
# df_description = pd.read_csv('../data/desc.csv')

out_recommendation = csv.writer(codecs.open("../data/batch_1/recommendation.csv", "w", "utf-8"), delimiter=",", quoting=csv.QUOTE_ALL)
out_recommendation.writerow(['Book Title','Book ISBN','Book URL','Amazon Price','R1 Title','R1 URL','R2 Title','R2 URL','R3 Title','R3 URL','R4 Title','R4 URL','R5 Title','R5 URL'])

list_amazon_list = list()

for row in read_description:

# good_reads_amazon_url = 'https://www.goodreads.com/buy_buttons/12/follow?book_id=4588&ref=x_gr_w_bb&tag=x_gr_w_bb-20'

    good_reads_amazon_url = row[2] #row['Amazon URL']

    # To handle amazon.in / amazon.ca / amazon.co.uk / amazon.fr links

    browser.get(good_reads_amazon_url)
    amazon_url = browser.current_url

    if '.com' not in amazon_url:
        if 'amazon.in' in amazon_url:
            amazon_url = amazon_url.replace('amazon.in', 'amazon.com')
            browser.get(amazon_url)
            time.sleep(2)

        elif 'amazon.ca' in amazon_url:
            amazon_url = amazon_url.replace('amazon.ca', 'amazon.com')
            browser.get(amazon_url)
            time.sleep(2)

        elif 'amazon.co.uk' in amazon_url:
            amazon_url = amazon_url.replace('amazon.co.uk', 'amazon.com')
            browser.get(amazon_url)
            time.sleep(2)

        elif 'amazon.fr' in amazon_url:
            amazon_url = amazon_url.replace('amazon.fr', 'amazon.com')
            browser.get(amazon_url)
            time.sleep(2)

        elif 'amazon.de' in amazon_url:
            amazon_url = amazon_url.replace('amazon.de', 'amazon.com')
            browser.get(amazon_url)
            time.sleep(2)

    time.sleep(2)

    amazon_price = get_amazon_price(amazon_url, True)
    r_list = get_amazon_recommendation(amazon_url, 5, True) #recommendation list
    amazon_description = get_amazon_description(amazon_url, True)

    # print(amazon_price)
    # print(amazon_description)
    # for i in r_list:
    #     print(i)

    row.append(amazon_description)
    out_description.writerow(row)


    r_list.insert(0, amazon_price)
    r_list.insert(0, row[2])#row['Amazon URL']
    r_list.insert(0, row[1])#row['ISBN'])
    r_list.insert(0, row[0])#row['Book Title'])
    out_recommendation.writerow(r_list)

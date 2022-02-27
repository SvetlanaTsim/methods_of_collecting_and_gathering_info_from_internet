from lxml import html
import requests
import pymongo
from pymongo.errors import *
from time import sleep
from bs4 import BeautifulSoup as BS
from datetime import datetime
import hashlib


class NewsScrapper:
    def __init__(self, db_name, collection_name):
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}
        self.lenta_url = 'https://lenta.ru/'
        self.mail_url = 'https://news.mail.ru/'
        self.mail_params = {'_ga': '2.49392421.2063121438.1645281594-1642862652.1639754562'}

    """method for parsing lenta.ru"""
    def lenta_parser(self):
        sleep(1)
        response = requests.get(self.lenta_url, headers=self.headers)
        dom = html.fromstring(response.text)
        news_list = []
        news = dom.xpath('//a[contains(@class,"card")]')
        for item in news:
            one_news = {}
            one_news['source_name'] = 'lenta.ru'
            one_news['news_name'] = item.xpath(".//*[contains(@class,'__title')]/text()")[0]
            one_news['link'] = item.xpath(".//@href")[0]
            if one_news['link'].find('http') == -1:
                one_news['link'] = self.lenta_url[:-1] + one_news['link']
            one_news['date'] = item.xpath(".//time[contains(@class,'__date')]//text()")
            news_list.append(one_news)
        for news in news_list:
            if news['date']:
                news['date'] = news['date'][0]
                date = news['date'].split(',')
                if len(date) < 2:
                    now = datetime.now()
                    date.append(now.strftime("%d/%m/%Y"))
                news['date'] = ' '.join(date)
            else:
                sleep(1)
                response_date = requests.get(self.lenta_url + news['link'], headers=self.headers)
                #xpath didn`t found, returned undefined
                dom = BS(response_date.text, 'html.parser')
                try:
                    date_time = dom.find('time', {'topic-header__item topic-header__time'}).text
                    news['date'] = date_time
                except AttributeError as e:
                    news['date'] = None
        return news_list

    """method for parsing main section of news.mail.ru"""
    def mail_news_parser(self):
        sleep(1)
        response = requests.get(self.mail_url, params=self.mail_params, headers=self.headers)
        dom = html.fromstring(response.text)
        first_block = dom.xpath('//div[@class="block"]')
        first_block_news = first_block[0].xpath('//a[contains(@class,"photo")] | //a[contains(@class,"list__text")]')
        news_list = []
        for item in first_block_news[:13]:
            one_news = {}
            one_news['news_name'] = item.xpath(".//text()")[0].replace('\xa0', ' ')
            one_news['link'] = item.xpath("./@href")[0]
            sleep(1)
            response_one = requests.get(one_news['link'], headers=self.headers)
            # xpath didn`t found, returned undefined
            dom_one = BS(response_one.text, 'html.parser')
            one_news['date'] = dom_one.find('span', {'note__text breadcrumbs__text js-ago'}).get('datetime').split('T')[0]
            one_news['source_name'] = dom_one.find('a', {'link color_gray breadcrumbs__link'}).text
            news_list.append(one_news)
        return news_list

    """method for parsing both lenta.ru and news.mail.ru"""
    def get_lenta_mail_news(self):
        news_data = []
        news_data.extend(self.lenta_parser())
        news_data.extend(self.mail_news_parser())
        return news_data

    """method for getting hashed id for news in order to avoid dublicating when inserting into databases"""
    def get_data_with_hash_id(self):
        data = self.get_lenta_mail_news()
        for i in data:
            data_for_hash = str(i['news_name']) + str(i['link']) + str(i['date']) + str(i['source_name'])
            data_bytes = data_for_hash.encode('utf-8')
            hash_object = hashlib.sha1(data_bytes)
            hex_dig = hash_object.hexdigest()
            i['_id'] = hex_dig
        return data

    """method for inserting news into databases"""
    def insert_news_to_database(self):
        news = self.get_data_with_hash_id()
        for i in news:
            try:
                self.collection.insert_one(i)
            except DuplicateKeyError as e:
                print(e)
                print('--> ', i['_id'], i['news_name'], i['source_name'], 'was duplicated')
        print('All news successfully inserted!')


a = NewsScrapper('news_db', 'lenta_mail')
a.insert_news_to_database()

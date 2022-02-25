from bs4 import BeautifulSoup as BS
import requests
import re
import pymongo
from pprint import pprint
from pymongo.errors import *
from time import sleep
import hashlib


class JobScrapper:
    def __init__(self, db_name, collection_name, vacancy_name):
        self.db_name = db_name
        self.collection_name = collection_name
        self.vacancy = vacancy_name
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}

        self.hh_url = 'https://hh.ru'
        self.hh_suffix = '/search/vacancy/'
        self.hh_params = {'area': 1,
                          'fromSearchLine': 'true',
                          'text': self.vacancy,
                          'page': 0,
                          'hhtmFrom': 'vacancy_search_list'}

        self.superjob_url = 'https://russia.superjob.ru'
        self.superjob_suffix = '/vacancy/search/'
        self.superjob_params = {'area': 1,
                               'keywords': self.vacancy,
                               'page': 1}

    """Метод для получения данных конкретной вакансии на сайте hh.ru"""
    def _hh_vacancy_parser(self, vacancy):
        sleep(1)
        vacancy_name = vacancy.find('span', {'class': 'resume-search-item__name'}).text
        company = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text.replace('\xa0', ' ')
        city = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text.split()[0].replace(',', '')
        vacancy_link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href')
        site = 'hh.ru'
        salary_info = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        salary_min = None
        salary_max = None
        currency = None
        if salary_info:
            salary = salary_info.text
            RE_DIGIT = re.compile(r'\d+[\s|\S]\d+\s\d*')
            RE_CURRENCY = re.compile(r'[р|Р][у|У][б|Б]|[u|U][s|S][d|D]|[e|E][u|U][r|R]|[r|R][u|U][b|B]')
            currency = RE_CURRENCY.search(salary).group().title()
            salary_amounts = RE_DIGIT.findall(str(salary))
            salary_amounts = list(map(lambda x: float(x.replace('\u202f', '')), salary_amounts))
            if len(salary_amounts) == 2:
                salary_min = salary_amounts[0]
                salary_max = salary_amounts[1]
            else:
                RE_ENDS_WITH = re.compile(r'[д|Д][о]')
                # находим, есть ли в описании вакансии слово "до"
                ends_with = RE_ENDS_WITH.search(str(salary))
                if ends_with:
                    # если да, то это - максимальная зп
                    salary_max = salary_amounts[0]
                else:
                    # если нет, то указываем как минимальную зп
                    salary_min = salary_amounts[0]

        vacancies_data = {'vacancy_name': vacancy_name,
                          'company': company,
                          'city': city,
                          'salary_min': salary_min,
                          'salary_max': salary_max,
                          'currency': currency,
                          'vacancy_link': vacancy_link,
                          'site': site}

        return vacancies_data

    """Метод для получения данных всех вакансий на одной странице на сайте hh.ru"""
    def _hh_page_parser(self, page):
        params = {'area': 1,
                  'fromSearchLine': 'true',
                  'text': self.vacancy,
                  'page': page,
                  'hhtmFrom': 'vacancy_search_list'}

        response = requests.get(self.hh_url + self.hh_suffix, params=params, headers=self.headers)
        dom = BS(response.text, 'html.parser')
        vacancies = dom.find_all('div', {'class': 'vacancy-serp-item vacancy-serp-item_redesigned'})
        vacancies_data = []

        for vacancy in vacancies:
            single_vacancy_data = self._hh_vacancy_parser(vacancy)
            vacancies_data.append(single_vacancy_data)

        return vacancies_data

    """Функция для получения данных всех вакансий всего сайта hh.ru"""
    def hh_parser(self):
        response = requests.get(self.hh_url + self.hh_suffix, params=self.hh_params, headers=self.headers)
        dom = BS(response.text, 'html.parser')
        last_page = int(dom.find('span', {'data-qa': 'pager-page-wrapper-40-39'}).text)
        all_vacancies_data = []

        for i in range(0, last_page):
            page_list = self._hh_page_parser(i)
            all_vacancies_data.extend(page_list)

        return all_vacancies_data

    """Метод для получения данных конкретной вакансии на сайте superjob.ru"""
    def _superjob_vacancy_parser(self, vacancy):
        sleep(1)
        vacancy_name = vacancy.find('span', {'class': '_3a-0Y _3DjcL _3sM6i'}).text
        company = vacancy.find('span', {
            'class': '_3Fsn4 f-test-text-vacancy-item-company-name _1_OKi _3DjcL _1tCB5 _3fXVo _2iyjv'})
        if company:
            company = company.text
        else:
            company = None
        city = \
            vacancy.find('span', {'class': 'f-test-text-company-item-location _1_OKi _3DjcL _1tCB5 _3fXVo'}).text.split('•')[1].replace(' ', '').split(',')[0]
        span_link = vacancy.find('span', {'class': '_3a-0Y _3DjcL _3sM6i'})
        link = self.superjob_url + span_link.findChildren(recursive=False)[0].get('href')
        site = 'superjob.ru'
        salary_info = vacancy.find('span', {'class': '_1OuF_ _1qw9T f-test-text-company-item-salary'}).text
        salary_min = None
        salary_max = None
        currency = None
        RE_DIGIT = re.compile(r'\d+[\s|\S]\d+')
        salary_amounts = RE_DIGIT.findall(str(salary_info))
        if salary_amounts:
            RE_CURRENCY = re.compile(r'[р|Р][у|У][б|Б]|[u|U][s|S][d|D]|[e|E][u|U][r|R]|[r|R][u|U][b|B]')
            currency = RE_CURRENCY.search(salary_info).group().title()
            salary_amounts = RE_DIGIT.findall(str(salary_info))
            salary_amounts = list(map(lambda x: float(x.replace('\xa0', '')), salary_amounts))
            if len(salary_amounts) == 2:
                salary_min = salary_amounts[0]
                salary_max = salary_amounts[1]
            else:
                RE_ENDS_WITH = re.compile(r'[д|Д][о]')
                # находим, есть ли в описании вакансии слово "до"
                ends_with = RE_ENDS_WITH.search(str(salary_info))
                if ends_with:
                    # если да, то это - максимальная зп
                    salary_max = salary_amounts[0]
                else:
                    # если нет, то указываем как минимальную зп
                    salary_min = salary_amounts[0]

        vacancies_data = {'vacancy_name': vacancy_name,
                          'company': company,
                          'city': city,
                          'salary_min': salary_min,
                          'salary_max': salary_max,
                          'currency': currency,
                          'vacancy_link': link,
                          'site': site}

        return vacancies_data

    """Метод для получения данных всех вакансий на одной странице на сайте superjob.ru"""
    def _superjob_page_parser(self, page):
        params = {'area': 1,
                  'keywords': self.vacancy,
                  'page': page}
        response = requests.get(self.superjob_url + self.superjob_suffix, params=params, headers=self.headers)
        dom = BS(response.text, 'html.parser')
        vacancies = dom.find_all('div', {'class': 'Fo44F QiY08 LvoDO'})
        vacancies_data = []

        for vacancy in vacancies:
            single_vacancy_data = self._superjob_vacancy_parser(vacancy)
            vacancies_data.append(single_vacancy_data)

        return vacancies_data

    """Метод для получения данных всех вакансий всего сайта superjob.ru"""
    def superjob_parser(self):
        response = requests.get(self.superjob_url + self.superjob_suffix, params=self.superjob_params, headers=self.headers)
        dom = BS(response.text, 'html.parser')
        last_page = int(dom.find('a', {'class': 'icMQ_ bs_sM _3ze9n l9LnJ f-test-button-9 f-test-link-9'}).text)
        all_vacancies_data = []

        for i in range(1, last_page + 1):
            page_list = self._superjob_page_parser(i)
            all_vacancies_data.extend(page_list)

        return all_vacancies_data

    """Метод возвращает список словарей с вакансиями с hh.ru и superjob.ru"""
    def get_all_vacancies_data(self):
        vacancies_data = []
        vacancies_data.extend(self.hh_parser())
        vacancies_data.extend(self.superjob_parser())
        return vacancies_data

    """Метод возвращает список словарей с вакансиями с hh.ru и superjob.ru 
    с id виде хэша суммы всех полей. Хэш создается уникальный и не позволит вставить 
    дублирующую запись"""
    def get_data_with_hash_id(self):
        data = self.get_all_vacancies_data()
        for i in data:
            data_for_hash = str(i['vacancy_name']) + str(i['company']) + str(i['city']) + str(i['salary_min']) + str(i['salary_max']) + \
                            str(i['currency']) + str(i['vacancy_link']) + str(i['site'])
            data_bytes = data_for_hash.encode('utf-8')
            hash_object = hashlib.sha1(data_bytes)
            hex_dig = hash_object.hexdigest()
            i['_id'] = hex_dig
        return data

    """Метод вставляет вакансии в базу данных"""
    def insert_vacancies_to_database(self):
        vacancies = self.get_data_with_hash_id()
        for vacancy in vacancies:
            try:
                self.collection.insert_one(vacancy)
            except DuplicateKeyError as e:
                print(e)
                print('--> ', vacancy['_id'], vacancy['vacancy_name'], vacancy['company'], 'was duplicated')
        print('All vacancies successfully inserted!')

    """Метод для поиска вакансий с зп больше указанной"""
    def find_vacancies_with_salary(self, salary):
        salary = float(salary)
        # логическое или
        for vacancy in self.collection.find({'$or': [{'salary_min': {'$gt': salary}}, {'salary_max': {'$gt': salary}}]}):
            pprint(vacancy)


a = JobScrapper('py_job', 'hh_sj_python', 'python')
a.insert_vacancies_to_database()
a.find_vacancies_with_salary(150000)

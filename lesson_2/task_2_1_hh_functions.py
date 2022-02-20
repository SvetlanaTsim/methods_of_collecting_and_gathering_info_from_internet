from bs4 import BeautifulSoup as BS
import pandas as pd
import requests
import re


"""Функция для получения данных конкретной вакансии на сайте hh.ru"""
def hh_vacancy_parser(vacancy):
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

"""Функция для получения данных всех вакансий на одной странице на сайте hh.ru"""
def hh_page_parser(page, text, url, suffix):
    url = url
    suffix = suffix
    params = {'area': 1,
              'fromSearchLine': 'true',
              'text': text,
              'page': page,
              'hhtmFrom': 'vacancy_search_list'}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}
    response = requests.get(url + suffix, params=params, headers=headers)
    dom = BS(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item vacancy-serp-item_redesigned'})
    vacancies_data = []

    for vacancy in vacancies:
        single_vacancy_data = hh_vacancy_parser(vacancy)
        vacancies_data.append(single_vacancy_data)

    return vacancies_data


"""Функция для получения данных всех вакансий всего сайта hh.ru"""
def hh_parser(text):
    url = 'https://hh.ru'
    suffix = '/search/vacancy/'
    params = {'area': 1,
              'fromSearchLine': 'true',
              'text': text,
              'page': 0,
              'hhtmFrom': 'vacancy_search_list'}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}

    response = requests.get(url + suffix, params=params, headers=headers)
    dom = BS(response.text, 'html.parser')
    last_page = int(dom.find('span', {'data-qa': 'pager-page-wrapper-40-39'}).text)
    all_vacancies_data = []

    for i in range(0, last_page):
        page_list = hh_page_parser(i, text, url, suffix)
        all_vacancies_data.extend(page_list)

    return all_vacancies_data


if __name__ == '__main__':
    all_vacancies_data = hh_parser('python')
    print(all_vacancies_data)
    # 800
    print(len(all_vacancies_data))

    df = pd.DataFrame(all_vacancies_data)
    print(df.head())

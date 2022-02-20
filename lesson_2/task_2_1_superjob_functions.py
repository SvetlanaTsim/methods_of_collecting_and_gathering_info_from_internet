from bs4 import BeautifulSoup as BS
import pandas as pd
import requests
import re


"""Функция для получения данных конкретной вакансии на сайте superjob.ru"""
def superjob_vacancy_parser(vacancy, url):
    vacancy_name = vacancy.find('span', {'class': '_3a-0Y _3DjcL _3sM6i'}).text
    company = vacancy.find('span', {'class': '_3Fsn4 f-test-text-vacancy-item-company-name _1_OKi _3DjcL _1tCB5 _3fXVo _2iyjv'})
    if company:
        company = company.text
    else:
        company = None
    city = vacancy.find('span', {'class': 'f-test-text-company-item-location _1_OKi _3DjcL _1tCB5 _3fXVo'}).text.split('•')[1].replace(' ', '').split(',')[0]
    span_link = vacancy.find('span', {'class': '_3a-0Y _3DjcL _3sM6i'})
    link = url + span_link.findChildren(recursive=False)[0].get('href')
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


"""Функция для получения данных всех вакансий на одной странице на сайте superjob.ru"""
def superjob_page_parser(page, text, url, suffix):
    url = url
    suffix = suffix
    params = {'area': 1,
              'keywords': text,
              'page': page}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}
    response = requests.get(url + suffix, params=params, headers=headers)
    dom = BS(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'Fo44F QiY08 LvoDO'})
    vacancies_data = []

    for vacancy in vacancies:
        single_vacancy_data = superjob_vacancy_parser(vacancy, url)
        vacancies_data.append(single_vacancy_data)

    return vacancies_data


"""Функция для получения данных всех вакансий всего сайта superjob.ru"""
def superjob_parser(text):
    url = 'https://russia.superjob.ru'
    suffix = '/vacancy/search/'
    params = {'area': 1,
              'keywords': 'python',
              'page': 1}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}
    response = requests.get(url + suffix, params=params, headers=headers)
    dom = BS(response.text, 'html.parser')
    last_page = int(dom.find('a', {'class': 'icMQ_ bs_sM _3ze9n l9LnJ f-test-button-8 f-test-link-8'}).text)
    all_vacancies_data = []

    for i in range(1, last_page+1):
        page_list = superjob_page_parser(i, text, url, suffix)
        all_vacancies_data.extend(page_list)

    return all_vacancies_data


if __name__ == '__main__':
    all_vacancies_data = superjob_parser('python')
    print(all_vacancies_data)
    # 159
    print(len(all_vacancies_data))

    df = pd.DataFrame(all_vacancies_data)
    print(df.head())

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
#from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class JobparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancy29032022

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min'], item['max'], item['cur'] = self.process_salary_hh(item['salary'])
        elif spider.name == 'sjru':
            item['min'], item['max'], item['cur'] = self.process_salary_sj(item['salary'])
        del item['salary']

        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def process_salary_hh(self, salary):
        min = None
        max = None
        cur = None
        if salary != ['з/п не указана']:
            salary = ''.join(salary)
            RE_DIGIT = re.compile(r'\d+[\s|\S]\d+\s\d*')
            RE_cur = re.compile(r'[р|Р][у|У][б|Б]|[u|U][s|S][d|D]|[e|E][u|U][r|R]|[r|R][u|U][b|B]')
            # cur = RE_cur.search(salary).group().title()
            cur = RE_cur.search(salary)
            if cur:
                cur = cur.group().title()
            salary_amounts = RE_DIGIT.findall(str(salary))
            salary_amounts = list(map(lambda x: float(x.replace('\u202f', '').replace('\xa0', '')), salary_amounts))
            #salary_amounts = list(map(lambda x: x.replace('\u202f', '').replace('\xa0', ''), salary_amounts))
            if len(salary_amounts) == 2:
                min = salary_amounts[0]
                max = salary_amounts[1]
            else:
                RE_ENDS_WITH = re.compile(r'[д|Д][о]')
                # находим, есть ли в описании вакансии слово "до"
                ends_with = RE_ENDS_WITH.search(str(salary))
                if ends_with:
                    # если да, то это - максимальная зп
                    max = salary_amounts[0]
                else:
                    # если нет, то указываем как минимальную зп
                    min = salary_amounts[0]
        return min, max, cur


    def process_salary_sj(self, salary):
        min = None
        max = None
        cur = None
        if salary != ['По договорённости']:
            salary = ''.join(salary)
            RE_DIGIT = re.compile(r'\d+[\s|\S]\d+')
            salary_amounts = RE_DIGIT.findall(str(salary))
            if salary_amounts:
                RE_CURRENCY = re.compile(r'[р|Р][у|У][б|Б]|[u|U][s|S][d|D]|[e|E][u|U][r|R]|[r|R][u|U][b|B]')
                cur = RE_CURRENCY.search(salary).group().title()
                salary_amounts = RE_DIGIT.findall(str(salary))
                salary_amounts = list(map(lambda x: float(x.replace('\xa0', '')), salary_amounts))
                if len(salary_amounts) == 2:
                    min = salary_amounts[0]
                    max = salary_amounts[1]
                else:
                    RE_ENDS_WITH = re.compile(r'[д|Д][о]')
                    # находим, есть ли в описании вакансии слово "до"
                    ends_with = RE_ENDS_WITH.search(str(salary))
                    if ends_with:
                        # если да, то это - максимальная зп
                        max = salary_amounts[0]
                    else:
                        # если нет, то указываем как минимальную зп
                        min = salary_amounts[0]
        return min, max, cur
    
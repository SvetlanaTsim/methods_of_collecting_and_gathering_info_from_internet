import pandas as pd
from task_2_1_hh_functions import hh_parser
from task_2_1_superjob_functions import superjob_parser

"""Функия возвращает Pandas DataFrame с вакансиями с hh.ru и superjob.ru"""
def get_all_vacancies_data(text):
    vacancies_data = []
    vacancies_data.extend(hh_parser(text))
    vacancies_data.extend(superjob_parser(text))
    df = pd.DataFrame(vacancies_data)
    return df

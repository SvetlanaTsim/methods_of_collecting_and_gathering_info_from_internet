import tempfile
import os
import zipfile
import pandas as pd
import pymongo
import requests
import json
from pymongo.errors import *


class OpenDataScrapper:
    def __init__(self, db_name, collection_name, url):
        self.url = url
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        self.dir_name = self.db_name + self.collection_name

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}

    '''method gets data from url and extracts from zip archive'''
    def get_data_from_url(self):
        response = requests.get('https://op.mos.ru/EHDWSREST/catalog/export/get?id=1306339')
        file = tempfile.TemporaryFile()
        file.write(response.content)
        fzip = zipfile.ZipFile(file)
        fzip.extractall(self.dir_name)
        file.close()
        fzip.close()
        return

    '''method return the name of file in the folder to where the file was downloaded'''
    def get_file_name(self):
        for element in os.scandir(self.dir_name):
            if element.is_file():
                return element.name

    '''method transforms data to dict from json'''
    def get_data_dict_from_json(self):
        self.get_data_from_url()
        path = f'{self.dir_name}/{self.get_file_name()}'
        with open(path, 'r', encoding="windows-1251") as f:
            data = json.loads(f.read())
        return data

    '''method inserts data to database'''
    def insert_data_to_database(self):
        data = self.get_data_dict_from_json()
        for item in data:
            try:
                self.collection.insert_one(item)
            except DuplicateKeyError as e:
                print(e)
                print('--> ', item, 'was duplicated')
        print('All data successfully inserted!')
        return

    '''method for extracting data from database according the field name and data name'''
    def find_data_in_field(self, field, data_name):
        datalist = []
        for data in self.collection.find({field: data_name}):
            datalist.append(data)
        return datalist

    '''method for getting csv file with extracted from database data according the field name and data name'''
    def get_csv_file_with_extracted_data(self, path, field, data_name):
        data = self.find_data_in_field(field, data_name)
        df = pd.DataFrame(data)
        print(df)
        df.to_csv(path)
        return


URL = 'https://op.mos.ru/EHDWSREST/catalog/export/get?id=1306339'
FIELD = 'AdmArea'
DATA_NAME = 'Северо-Восточный административный округ'
PATH = 'extract/result.csv'


data_mos = OpenDataScrapper('data_mos', 'bike_parking_05042022', URL)
data_mos.insert_data_to_database()
# data_mos.find_data_in_field(FIELD, DATA_NAME)
data_mos.get_csv_file_with_extracted_data(PATH, FIELD, DATA_NAME)

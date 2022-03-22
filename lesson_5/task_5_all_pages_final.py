import pymongo
from pymongo.errors import *
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import hashlib


class MailScrapper:
    def __init__(self, db_name, collection_name, login, password):
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        self.login = login
        self.password = password
        self.driver = webdriver.Chrome(executable_path='./chromedriver.exe')

    """method for entering mail.ru mailbox"""
    def enter_mailbox(self):
        self.driver.get('https://account.mail.ru/login?page=https%3A%2F%2Fe.mail.ru%2Finbox%3Futm_source%3Dportal%26utm_medium%3Dmailbox%26utm_campaign%3De.mail.ru%26mt_click_id%3Dmt-veoz41-1647853654-3521283880&allow_external=1&from=octavius')
        self.driver.implicitly_wait(10)
        elem = self.driver.find_element(By.TAG_NAME, 'input')
        elem.send_keys(self.login)
        elem.send_keys(Keys.ENTER)

        self.driver.implicitly_wait(10)
        password = self.driver.find_element(By.XPATH, '//input[contains(@name,"password")]')
        password.send_keys(self.password)
        password.send_keys(Keys.ENTER)

    """method for getting links of the letters"""
    def get_letters_links(self):
        self.enter_mailbox()
        link_set = set()
        last_letter = None
        while True:
            self.driver.implicitly_wait(100)
            letters = self.driver.find_elements(By.CLASS_NAME, 'js-tooltip-direction_letter-bottom')
            new_last_letter = letters[-1]
            actions = ActionChains(self.driver)
            for letter in letters:
                links = letter.get_attribute("href")
                link_set.add(links)
            actions.move_to_element(letters[-1])
            actions.perform()
            time.sleep(2)
            if new_last_letter == last_letter:
                break
            last_letter = letters[-1]
        return link_set

    """method for parsing of all the letters"""
    def letters_parse(self):
        link_set = self.get_letters_links()
        all_letters_list = []
        for link in link_set:
            letter_dict = {}
            time.sleep(2)
            self.driver.implicitly_wait(100)
            self.driver.get(link)
            letter_dict['from_person'] = self.driver.find_element(By.CLASS_NAME, 'letter-contact').text
            letter_dict['from_email'] = self.driver.find_element(By.CLASS_NAME, 'letter-contact').get_attribute("title")
            letter_dict['date'] = self.driver.find_element(By.CLASS_NAME, 'letter__date').text
            letter_dict['subject'] = self.driver.find_element(By.CLASS_NAME, 'thread-subject').text
            letter_dict['letter_text'] = self.driver.find_element(By.CLASS_NAME, 'letter__body')\
                .text.replace('\n', ' ').replace('\u200c\u2005', '').replace('\u200c', '')
            all_letters_list.append(letter_dict)
        self.driver.quit()
        return all_letters_list

    """method for getting hashed id for letters in order to avoid dublicating when inserting into databases"""
    def get_data_with_hash_id(self):
        data = self.letters_parse()
        for i in data:
            data_for_hash = str(i['from_person']) + str(i['from_email']) + str(i['date']) + str(i['subject']) \
                            + str(i['letter_text'])
            data_bytes = data_for_hash.encode('utf-8')
            hash_object = hashlib.sha1(data_bytes)
            hex_dig = hash_object.hexdigest()
            i['_id'] = hex_dig
        return data

    """method for inserting letters into databases"""
    def insert_letters_to_database(self):
        letters = self.get_data_with_hash_id()
        for i in letters:
            try:
                self.collection.insert_one(i)
            except DuplicateKeyError as e:
                print(e)
                print('--> ', i['_id'], i['from_person'], i['subject'], 'was duplicated')
        print('All letters successfully inserted!')


current_letters = MailScrapper('mail_db_new', 'mail_letters_new', 'gb_students_787@mail.ru', 'Gfhjkmlkzcneltynjd001#')
current_letters.insert_letters_to_database()

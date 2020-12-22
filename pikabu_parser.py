from abc import ABC, abstractmethod

from webdriver_manager.chrome import ChromeDriverManager

from main_parser import Web_Parser
from pymongo import MongoClient, errors
from selenium import webdriver
from bs4 import BeautifulSoup
from threading import Thread

import hashlib
import re
import html5lib
import html
import requests
import time
import logging
import json


class Pikabu_Parser(Web_Parser):
    def __init__(self, urls):
        super().__init__(urls)

    def get_webdriver(self, path_to_webdriver_binary: str, is_headless: bool = True):

        options = webdriver.ChromeOptions()

        if is_headless:  # для открытия браузера без открытия окна
            options.add_argument('headless')

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)

    def get_db_collection(self):
        client = MongoClient("mongodb://woipot:woipot@aqulasoft.com/daryana")
        self.clinent = client
        db = client.web_parser
        self.db_collection = db.pikabu

    def start_parse(self):
        for url in self.urls:
            self.__get_content__(html.unescape(url))

        self.driver.quit()
        self.clinent.close()

    def __get_content__(self, url):
        logging.info(url)
        self.driver.get(url)

        SCROLL_PAUSE_TIME = 5

        # Get scroll height
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        i = 0
        while True:
            # while i < 2:
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height
            i += 1
            logging.info(f'Iterations made: {i}')

            # Получение HTML-содержимого
            requiredHtml = self.driver.page_source
            self.__parse_page__(requiredHtml)

        logging.info(f'Total iterations made: {i}')

    def __parse_page__(self, requiredHtml):

        soup = BeautifulSoup(requiredHtml, 'html5lib')

        g_data = soup.find_all("div", {"class": "story__main"})
        logging.info(f'Stories found: {len(g_data)}')

        for item in g_data:

            urls = item.find_all("h2", {"class": "story__title"})
            contents = item.find_all("div", {"class": "story__content-inner"})

            for (url, content) in zip(urls, contents):

                story = dict(_id=url.find('a').get('href'),
                             content=re.sub(r'[\t\v\r\n\f]+', ' ', content.text))

                if len(story["content"]) > 300:
                    self.__load_to_db__(story)
                    # self.__load_to_file__(
                    #     story=story, filename='pikabu_stories.txt')

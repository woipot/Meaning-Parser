from abc import ABC, abstractmethod

from webdriver_manager.chrome import ChromeDriverManager

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


class Pikabu_Parser():
    def __init__(self, urls):
        self.urls = urls

    def get_webdriver(self, path_to_webdriver_binary: str, is_headless: bool = True):

        options = webdriver.ChromeOptions()

        if is_headless:
            options.add_argument('headless')

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)

    def get_db_collection(self):
        client = MongoClient(
            "mongodb://aqulasoft:aqulasoft1@185.246.152.112/daryana")
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

        SCROLL_PAUSE_TIME = 7

        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        i = 0
        while True:

            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(SCROLL_PAUSE_TIME)

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height
            i += 1
            logging.info(f'Iterations made: {i}')

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
                             content=re.sub(r'[\t\v\r\n\f]+',
                                            ' ', content.text),
                             meaning='')

                if len(story["content"]) > 300:
                    self.__load_to_db__(story)

    def __load_to_db__(self, story: dict) -> None:
        try:
            self.db_collection.insert_one(story)
            logging.info(f'Stories in DB: {self.db_collection.count()}')
        except errors.DuplicateKeyError:
            return

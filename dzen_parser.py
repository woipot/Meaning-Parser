from abc import ABC, abstractmethod
from pprint import pprint
from main_parser import Web_Parser
from pymongo import MongoClient, errors
from selenium import webdriver
from bs4 import BeautifulSoup
from threading import Thread

import hashlib
import re
import html5lib
import requests
import time
import logging
import json
import html

import re

def str_contains_url(string):
    regex = r"(?i)\b(^https?://zen.yandex.ru/)"
    url = re.findall(regex,string)
    return [x[0] for x in url]


class Dzen_Parser(Web_Parser):
    def __init__(self, urls):
        super().__init__(urls)
        self.stories_urls = set()
        self.old_stories_urls = set()
        self.all_tags = set()

    def get_webdriver(self, path_to_webdriver_binary: str, is_headless: bool = True):

        options = webdriver.ChromeOptions()

        if is_headless:  # для открытия браузера без открытия окна
            options.add_argument('headless')

        self.driver = webdriver.Chrome(
            path_to_webdriver_binary, options=options)

    def get_db_collection(self):
        client = MongoClient("mongodb://woipot:woipot@185.246.152.112/daryana")
        self.client = client
        db = client.web_parser
        self.db_collection = db.dzen

    def start_parse(self):
        self.maxLimit = 300
        self.limit = 0
        for url in self.urls:
            # if (not str_contains_url(url)):
            #     next
            self.__get_content__(html.unescape(url))

        for url in self.stories_urls:
            # if str_contains_url(url):
            #     self.driver.get(url)
            #     requiredHtml = self.driver.page_source
            # else:
            logging.info(url)

        self.driver.quit()
        self.client.close()

    def __get_content__(self, url):
        logging.info(url)
        self.driver.get(url)

        SCROLL_PAUSE_TIME = 2

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
            self.__get_urls__(requiredHtml)
            if self.limit > self.maxLimit:
                break

        logging.info(f'Total iterations made: {i}')

    def __get_urls__(self, requiredHtml):
        soup = BeautifulSoup(requiredHtml, 'html5lib')

        g_data = soup.find_all(
            "a", {"class": "card-image-view-by-metrics__clickable"})
        logging.info(f'Stories found: {len(g_data)}')

        self.limit += len(g_data)
        for item in g_data:
            url = item.get('href')
            self.stories_urls.add(url)

    def __parse_story__(self, requiredHtml, url):

        soup = BeautifulSoup(requiredHtml, 'html5lib')

        g_data = soup.find_all(
            "div", {"id": "article__page-root"})

        for item in g_data:

            contents = item.find_all("div", {"class": "article-render"})

            for content in contents:
                text = []
                for p in content.find_all("p", {"class": "article-render__block article-render__block_unstyled"}):
                    text.append(re.sub(r'[\t\v\r\n\f]+', ' ', p.text))

                story = dict(_id=url,
                             content=" ".join(text).replace('\"', ''))
                if len(story["content"]) > 10:
                    self.__load_to_db__(story)
                    # self.__load_to_file__(
                    #     story=story, filename='dzen_stories.txt')

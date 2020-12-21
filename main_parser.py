from abc import ABC, abstractmethod
from pymongo import MongoClient, errors
from selenium import webdriver
from bs4 import BeautifulSoup

import hashlib
import re
import html
import html5lib
import requests
import time
import logging
import json

class Web_Parser(ABC):
    def __init__(self, urls):
        self.urls = urls

    @abstractmethod
    def get_webdriver(self, is_headless: bool = True, path_to_webdriver_binary: str = 'yandexdriver.exe'):
        pass

    @abstractmethod
    def get_db_collection(self):
        pass

    @abstractmethod
    def __get_content__(self, url: str):
        pass

    @abstractmethod
    def start_parse(self):
        pass

    def __load_to_db__(self, story: dict) -> None:
        try:
            self.db_collection.insert_one(story)
            logging.info(f'Stories in DB: {self.db_collection.count()}')
        except errors.DuplicateKeyError:
            return

    def __load_to_file__(self, story: dict, filename: str = 'all_stories.txt'):
        with open(filename, 'a', encoding='utf-8') as f:
            line = json.dumps(story, ensure_ascii=False)
            f.write(f'{line}\n')

    def __get_from_file__(self, filename: str = 'all_stories.txt'):

        with open(filename, 'r', encoding='utf-8') as f:
            while True:
                line = f.readline()
                if not line:
                    break

                yield json.loads(line)

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
import string


import nltk
# from nltk.tokenize import sent_tokenize, word_tokenize
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

print(morph.parse('KDE')[0].normal_form)


class Article_Parser():
    def __init__(self):
        self.client = MongoClient(
            "mongodb://woipot:woipot@185.246.152.112/daryana")
        db = self.client.web_parser
        self.db_collection = db.pikabu
        self.db_res_collection = db.parsed_article

    def __del__(self):
        self.client.close()

    def readFromDB(self):
        self.db_res_collection.drop()
        print(self.db_collection.count())
        for article in self.db_collection.find():
            a = article['content'].translate(
                str.maketrans('', '', string.punctuation))
            words = {}
            a_words = a.split()
            for word in a_words:
                p = morph.parse(word)[0].normal_form
                words[p] = (words[p] + 1) if p in words else 1

            res_article = dict(
                _id=article['_id'], words={}, word_count=len(a_words))
            for key, value in words.items():
                res_article['words'][key] = dict(
                    count=value, tf=value / len(a_words))
            self.db_res_collection.insert_one(res_article)

            # return

    # def parseArticle(self):
    #     json.

    def __load_to_db__(self, story: dict) -> None:
        try:
            self.db_collection.insert_one(story)
            logging.info(f'Stories in DB: {self.db_collection.count()}')
        except errors.DuplicateKeyError:
            return

import emoji
from sklearn.feature_extraction.text import TfidfVectorizer
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
from nltk.tokenize import sent_tokenize, word_tokenize
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

print(morph.parse('KDE')[0].normal_form)


def give_emoji_free_text(text):
    allchars = [str for str in text.decode('utf-8')]
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    clean_text = ' '.join([str for str in text.decode(
        'utf-8').split() if not any(i in str for i in emoji_list)])
    return clean_text


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
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   u"\U0001f926-\U0001f937"
                                   u"\u200d"
                                   u"\u2640-\u2642"
                                   "]+", flags=re.UNICODE)
        self.db_res_collection.drop()
        print(self.db_collection.count())
        all_a = []
        cou = 0
        for article in self.db_collection.find():

            a = give_emoji_free_text(article['content'].encode('utf8'))
            words = {}
            a_words = word_tokenize(a, language="russian")

            text = ' '

            for word in a_words:
                p = morph.parse(word.translate(
                    str.maketrans('', '', string.punctuation)))[0]
                functors_pos = {'INTJ', 'PRCL', 'CONJ',
                                'PREP', 'NPRO', 'NUMR'}
                if p.tag.POS is not None and p.tag.POS not in functors_pos:
                    text += p.normal_form + ' '
            cou += 1
            print(str(cou) + '\n')
            if cou > 50:
                break
            all_a.append(text)

        tfidf_vectorizer = TfidfVectorizer()
        values = tfidf_vectorizer.fit_transform(all_a)
        f_names = tfidf_vectorizer.get_feature_names()
        shape = print(values.shape)
        print(json.dumps(values))

    def __load_to_db__(self, story: dict) -> None:
        try:
            self.db_collection.insert_one(story)
            logging.info(f'Stories in DB: {self.db_collection.count()}')
        except errors.DuplicateKeyError:
            return

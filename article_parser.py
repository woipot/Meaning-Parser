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
            "mongodb://forichok:forichok1@185.246.152.112/daryana")
        db = self.client.web_parser
        self.db_collection = db.pikabu
        self.db_res_collection = db.parsed_article

    def __del__(self):
        self.client.close()

    def readFromDB(self):
        self.db_res_collection.drop()
        print(self.db_collection.count())
        all_a = []
        for article in self.db_collection.find():

            text = self.clearContent(article['content'])

            all_a.append(text)
            if len(all_a) > 50:
                print(len(all_a))
                break

        tfidf_vectorizer = TfidfVectorizer()
        values = tfidf_vectorizer.fit_transform(all_a)
        f_names = tfidf_vectorizer.get_feature_names()
        shape = print(values.shape)
        print(json.dumps(values))

    def clearContent(self, content: string):
        a = give_emoji_free_text(content.encode('utf8'))
        a_words = word_tokenize(a, language="russian")

        text = ' '

        for word in a_words:
            p = morph.parse(word.translate(
                str.maketrans('', '', string.punctuation)))[0]
            functors_pos = {'INTJ', 'PRCL', 'CONJ',
                            'PREP', 'NPRO', 'NUMR'}
            if p.tag.POS is not None and p.tag.POS not in functors_pos:
                text += p.normal_form + ' '
        return text

    def createDefaultSet(self, dict):
        tfidf_vectorizer = TfidfVectorizer(use_idf=True)
        for meaning in dict:
            meaningArticles = []
            for articleUrl in dict[meaning]:
                text = self.__load_from_db__(articleUrl)
                if text is None:
                    continue

                meaningArticles.append(self.clearContent(text['content']))
            values = tfidf_vectorizer.fit_transform(meaningArticles)
            f_names = tfidf_vectorizer.get_feature_names()




        pass

    def __load_from_db__(self, _id: string) -> string:

        try:
            texts = [i for i in self.db_collection.find({"_id": _id})]
            if len(texts) > 0:
                return texts[0]

            return None
        except Exception:
            return None

    def __load_to_db__(self, story: dict) -> None:
        try:
            self.db_collection.insert_one(story)
            logging.info(f'Stories in DB: {self.db_collection.count()}')
        except errors.DuplicateKeyError:
            return

from wordcloud import WordCloud
from os import path
import os
from nltk.probability import FreqDist
from collections import defaultdict
from collections import Counter
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import numpy as np
from random import randint
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from nltk.corpus import stopwords
import json
import re
import ssl
import string

import emoji
import nltk
import pandas as pd
import pymorphy2
from nltk.tokenize import word_tokenize
from pymongo import MongoClient, errors
from sklearn.feature_extraction.text import TfidfVectorizer

morph = pymorphy2.MorphAnalyzer()

print(morph.parse('KDE')[0].normal_form)


classifiers = [
    KNeighborsClassifier,
    SGDClassifier,
    RandomForestClassifier
]

classifier_dict = {
    KNeighborsClassifier: [],
    SGDClassifier: [],
    RandomForestClassifier: []
}

counts_classifiers_dict = {
    KNeighborsClassifier: [],
    SGDClassifier: [],
    RandomForestClassifier: []
}


def write_to_file(texts, labels, name):
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    with open(path.join(d, "classifier", name), 'w') as f:
        for i, text in enumerate(texts):
            f.write(f"{texts[i]}\n")
            f.write(f"{labels[i]}\n")


def get_max_and_avg(list_):
    if list_:
        return max(list_), sum(list_) / len(list_)


def giveEmojiFreeText(text: string) -> string:
    """
    part of text clean function

    :param text: text with emoji
    :return: text without emoji
    """
    allchars = [str for str in text.decode('utf-8')]
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    clean_text = ' '.join([str for str in text.decode(
        'utf-8').split() if not any(i in str for i in emoji_list)])
    return clean_text


def defaultFitFunction(headDict: dict, meaningsDefSet: dict) -> string:
    """
    MAIN function to predict article meaning

    :param headDict: TF of concrete article
    :param meaningsDefSet: meanings with TF-IDF
    :return: article meaning
    """
    meaningsMathDict = dict()

    for meaning in meaningsDefSet:
        value = None
        for defWord in meaningsDefSet[meaning]:
            defWordValue = meaningsDefSet[meaning][defWord]
            if defWord in headDict.keys():
                if value is None:
                    value = abs(defWordValue - headDict[defWord])
                else:
                    value += abs(defWordValue - headDict[defWord])

        if value is not None:
            meaningsMathDict[meaning] = value

    resultMeaning = 'Undefined'
    resultValue = None
    for meaning in meaningsMathDict:
        if resultValue is None or meaningsMathDict[meaning] < resultValue:
            resultValue = meaningsMathDict[meaning]
            resultMeaning = meaning

    print(
        f'Meaning = {resultMeaning}; near in (best match is 0): {resultValue}')
    return None if resultValue is None else resultMeaning


def calculateTfidf(documents: list):
    """
    see TfidfVectorizer of sklearn.feature_extraction.text documentations

    :param documents: a list of documents
    :return: TF-IDF dict head
    """
    tfidf_vectorizer = TfidfVectorizer(use_idf=True)
    values = tfidf_vectorizer.fit_transform(documents)
    df = pd.DataFrame(values[0].T.todense(
    ), index=tfidf_vectorizer.get_feature_names(), columns=["TF-IDF"])
    df = df.sort_values('TF-IDF', ascending=False)
    return df.head(30)


class ArticleParser():
    def __init__(self, dbConnectionString: string):
        """
            initialize mongo Data Base and download nltk packages
            :param dbConnectionString: provide connection string to working db
        """
        self.client = MongoClient(dbConnectionString)
        db = self.client.daryana1
        """!IMPORTANT USING PIKABU COLLECTION FROM DB NOW"""
        self.db_collection = db.pikabu
        self.db_res_collection = db.parsed_article
        self.def_set_collection = db.def_set_parsed_articles

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('russian'))

    def classify(self, limit: int) -> dict:
        story = dict(_id='id1',
                     content="content", meaning='meaning')
        # texts = [i for i in self.db_res_collection.find()]
        # self.db_collection.insert_one(story)
        articles = []
        opinions = []
        count = 0
        for article in self.db_collection.find():
            if "meaning" not in article or "content" not in article:
                continue

            if article['meaning'] == 'meaning':
                continue
            if count >= limit:
                break
            count = count+1
            articles.append(self.clearContent(article['content']))
            opinions.append(article['meaning'])

        j = 10
        print(len(articles))
        for classifier in classifiers:
            text_clf = Pipeline([
                                ('tfidf', TfidfVectorizer()),
                                ('clf', classifier())
                                ])

            for i in range(j):
                tmp = articles.copy()
                tmp_labels = opinions.copy()
                randomed = randint(0, len(articles)-j)
                basic_texts = tmp[randomed:randomed+j]
                basic_labels = tmp_labels[randomed:randomed+j]
                print(i)
                text_clf.fit(basic_texts, basic_labels)
                del tmp[randomed:randomed+len(basic_texts)]
                del tmp_labels[randomed:randomed+len(basic_texts)]
                predict = tmp.copy()
                predicted = text_clf.predict(predict)
                classifier_dict[classifier].append(
                    accuracy_score(tmp_labels, predicted))
                c = Counter(predicted)
                counts_classifiers_dict[classifier].append(
                    [c['мошеничество'], c['технологии'], c['глупые пользователи'], c['проблема'], c['ремонт']])
            write_to_file(
                tmp, tmp_labels, f"{classifier}_{accuracy_score(tmp_labels, predicted)}")

        for classifier in classifier_dict.keys():
            print(classifier, get_max_and_avg(classifier_dict[classifier]))

        for classifier in counts_classifiers_dict.keys():
            print(classifier, counts_classifiers_dict[classifier])

    def __del__(self):
        self.client.close()

    def clearContent(self, content: string) -> string:
        """
        clean article to make possible calculate TF-IDF and other calculations

        :param content: article content
        :return: raw article content (without unnecessary)
        """
        a = giveEmojiFreeText(content.encode('utf8'))
        a_words = word_tokenize(a, language="russian")

        text = ' '
        pattern = re.compile("^[^\d\W]+$")

        for word in a_words:
            if word not in self.stop_words and pattern.match(word):
                p = morph.parse(word.translate(
                    str.maketrans('', '', string.punctuation)))[0]
                functors_pos = {'INTJ', 'PRCL', 'CONJ',
                                'PREP', 'NPRO', 'NUMR'}
                if p.tag.POS is not None and p.tag.POS not in functors_pos:
                    text += p.normal_form + ' '
        return text

    def createDefaultSet(self, meaningsDict):
        """
        This function take dictionary with articles and calculate TF-IDF HEAD to predict
        meaning of any other articles in future
        this predict set will be saved in database

        !IMPORTANT you need to create first set by yourself (meanings.json for example)

        :param meaningsDict: provide dict in next form ->
        {
            "ANY MEANING": ["lINK TO ARTICLE"]
        }
        """
        self.db_res_collection.drop()
        self.def_set_collection.drop()

        for meaning in meaningsDict:
            meaningArticles = []
            for articleUrl in meaningsDict[meaning]:
                text = self.loadStoryFromDb(articleUrl)
                if text is None:
                    continue

                meaningArticles.append(self.clearContent(text['content']))

            print("\n" + meaning)
            head = calculateTfidf(meaningArticles)
            self.saveMeaningValuesToDb(meaning, head)
            print(head)
            self.saveDefUrlSetToDb(meaning, meaningsDict[meaning])

    def fitToDefaultSet(self, limit: int) -> dict:
        """
        this function use default set from method ArticleParser.createDefaultSet and predict meaning of part
        of articles from database to generate new training set for improve accuracy of predictions

        :param limit: articles limit
        :return: dict meanings with articles
        """
        meaningsDefUrls = self.loadDefUrlSetFromDb()
        meaningsDefSet = self.loadMeaningValuesFromDb()
        if meaningsDefSet is None:
            return

        parsedCount = 0
        for article in self.db_collection.find():
            presentInArticle = False
            for meaning in meaningsDefUrls:
                if article['_id'] in meaningsDefUrls[meaning]:
                    print(f"Skip article : {article['_id']}")
                    presentInArticle = True
                    break
            if presentInArticle:
                continue

            if 'content' not in article.keys():
                continue

            text = self.clearContent(article['content'])
            head = calculateTfidf([text])
            # print("\n\n" + article['_id'])
            # print(head)
            headDict = head['TF-IDF']

            articleMeaning = self.articleMeaning(headDict, meaningsDefSet)
            if articleMeaning is None:
                continue

            meaningsDefUrls[articleMeaning].append(article['_id'])
            print(
                f"#{parsedCount}: {article['_id']} add to -> {articleMeaning}")

            parsedCount += 1
            if parsedCount > limit:
                break
        return meaningsDefUrls

    @staticmethod
    def articleMeaning(words: dict, meaningsDefSet: dict) -> string:
        """
        stub to easy change a predict function

        :param words: TF_IDF data set of article
        :param meaningsDefSet: TF-IDF of default dict meanings
        :return: predicted article meaning
        """
        return defaultFitFunction(words, meaningsDefSet)

    def selfTeaching(self, articlesMaxCount: int, blockSize: int):
        """
        this function update default TF-IDF data set by parsing articles blocks
        to improve accuracy of prediction. This function only a facade for fitToDefaultSet function

        :param articlesMaxCount: articles to parse (the more the better)
        :param blockSize: teaching block (the less the better [blockSize > then your first default teach block])
        """
        iteration = 1

        if articlesMaxCount < blockSize:
            currentBlock = articlesMaxCount
        else:
            currentBlock = blockSize

        while articlesMaxCount > 0:
            articlesMaxCount -= currentBlock

            fitedList = self.fitToDefaultSet(currentBlock)
            print(f"#{iteration}: New DEFAULT set is ready")
            for i in fitedList:
                print(f"{i} : {len(fitedList[i])}")

            self.createDefaultSet(fitedList)

            iteration += 1
            if articlesMaxCount < blockSize:
                currentBlock = articlesMaxCount
            else:
                currentBlock = blockSize

    def saveMeaningValuesToDb(self, meaning, dataFrame) -> None:
        try:
            self.db_res_collection.insert_one(
                dict(_id=meaning, words=dataFrame.to_json(force_ascii=False)))
        except errors.DuplicateKeyError:
            return

    def loadMeaningValuesFromDb(self):
        try:
            texts = [i for i in self.db_res_collection.find()]
            if len(texts) > 0:
                textsRepairedFromJson = dict()
                for meaning in texts:
                    textsRepairedFromJson[meaning['_id']] = json.loads(meaning['words'])[
                        'TF-IDF']
                return textsRepairedFromJson

            return None
        except Exception:
            return None
        pass

    def saveDefUrlSetToDb(self, id, listUrls) -> None:
        try:
            self.def_set_collection.insert_one(
                dict(_id=id, urls=json.dumps(listUrls)))
        except errors.DuplicateKeyError:
            return

    def loadDefUrlSetFromDb(self):
        try:
            meanings = [i for i in self.def_set_collection.find()]
            if len(meanings) > 0:
                textsRepairedFromJson = dict()
                for meaning in meanings:
                    textsRepairedFromJson[meaning['_id']
                                          ] = json.loads(meaning['urls'])
                return textsRepairedFromJson
            return None
        except Exception:
            return None
        pass

    def loadStoryFromDb(self, _id: string) -> string:

        try:
            texts = [i for i in self.db_collection.find({"_id": _id})]
            if len(texts) > 0:
                return texts[0]

            return None
        except Exception:
            return None

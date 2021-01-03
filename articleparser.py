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
from nltk.corpus import stopwords

print(morph.parse('KDE')[0].normal_form)


def giveEmojiFreeText(text):
    allchars = [str for str in text.decode('utf-8')]
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    clean_text = ' '.join([str for str in text.decode(
        'utf-8').split() if not any(i in str for i in emoji_list)])
    return clean_text


def defaultFitFunction(headDict, meaningsDefSet):
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

    print(f'Meaning = {resultMeaning}; near in (best match is 0): {resultValue}')
    return None if resultValue is None else resultMeaning


class ArticleParser():
    def __init__(self):
        self.client = MongoClient(
            "mongodb://forichok:forichok1@185.246.152.112/daryana")
        db = self.client.web_parser
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

    def __del__(self):
        self.client.close()

    def readFromDB(self):
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
            head = self.calculateTfidf(meaningArticles)
            self.saveMeaningValuesToDb(meaning, head)
            print(head)
            self.saveDefUrlSetToDb(meaning, meaningsDict[meaning])

    def fitToDefaultSet(self, limit):
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

            text = self.clearContent(article['content'])
            head = self.calculateTfidf([text])
            # print("\n\n" + article['_id'])
            # print(head)
            headDict = head['TF-IDF']

            articleMeaning = self.articleMeaning(headDict, meaningsDefSet)
            if articleMeaning is None:
                continue

            meaningsDefUrls[articleMeaning].append(article['_id'])
            print(f"#{parsedCount}: {article['_id']} add to -> {articleMeaning}")

            parsedCount += 1
            if parsedCount > limit:
                break
        return meaningsDefUrls

    def calculateTfidf(self, documents):
        tfidf_vectorizer = TfidfVectorizer(use_idf=True)
        values = tfidf_vectorizer.fit_transform(documents)
        df = pd.DataFrame(values[0].T.todense(), index=tfidf_vectorizer.get_feature_names(), columns=["TF-IDF"])
        df = df.sort_values('TF-IDF', ascending=False)
        return df.head(30)

    def articleMeaning(self, words, meaningsDefSet):
        return defaultFitFunction(words, meaningsDefSet)

    def saveMeaningValuesToDb(self, meaning, dataFrame) -> None:
        try:
            self.db_res_collection.insert_one(dict(_id=meaning, words=dataFrame.to_json(force_ascii=False)))
        except errors.DuplicateKeyError:
            return

    def loadMeaningValuesFromDb(self):
        try:
            texts = [i for i in self.db_res_collection.find()]
            if len(texts) > 0:
                textsRepairedFromJson = dict()
                for meaning in texts:
                    textsRepairedFromJson[meaning['_id']] = json.loads(meaning['words'])['TF-IDF']
                return textsRepairedFromJson

            return None
        except Exception:
            return None
        pass

    def saveDefUrlSetToDb(self, id, listUrls) -> None:
        try:
            self.def_set_collection.insert_one(dict(_id=id, urls=json.dumps(listUrls)))
        except errors.DuplicateKeyError:
            return

    def loadDefUrlSetFromDb(self):
        try:
            meanings = [i for i in self.def_set_collection.find()]
            if len(meanings) > 0:
                textsRepairedFromJson = dict()
                for meaning in meanings:
                    textsRepairedFromJson[meaning['_id']] = json.loads(meaning['urls'])
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

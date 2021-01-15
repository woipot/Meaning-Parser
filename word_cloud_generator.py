import os
import json

from os import path
from wordcloud import WordCloud


def generateImgs():
    # d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    # text = open(path.join(d, filename)).read()
    # meanings = json.loads(text)
    # for key, value in meanings.items():
    #     generate(key, value, pref)

    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    kneibPath = path.join(d, "classifier", "KNeighborsClassifier")
    SGDPath = path.join(d, "classifier", "SGDClassifier")
    ForestPath = path.join(d, "classifier", "RandomForestClassifier")
    generateFromFile(kneibPath, "KNeighborsClassifier")
    generateFromFile(SGDPath, "SGDClassifier")
    generateFromFile(ForestPath, "RandomForestClassifier")


def generateFromFile(path, classifierName):
    articles = {}
    parsedArticles = {}
    with open(path, 'r') as content_file:
        content_list = content_file.read().strip().split("\n")
        count = 0
        while count < len(content_list):
            content = content_list[count]
            meaning = content_list[count + 1]
            count = count + 2
            if meaning not in articles:
                articles[meaning] = ""

            articles[meaning] = articles[meaning] + " " + content
        for key, value in articles.items():
            if key not in parsedArticles:
                parsedArticles[key] = {}

            words = value.strip().split(" ")

            for word in words:
                if word not in parsedArticles[key]:
                    parsedArticles[key][word] = 1
                else:
                    parsedArticles[key][word] = parsedArticles[key][word] + 1
            generate(key, parsedArticles[key], classifierName)
    print('log')


def generate(meaning, data, pref):
    wordcloud = WordCloud(max_words=20).generate_from_frequencies(data)
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    wordcloud.to_file(path.join(d, 'img/' + pref + "_" + meaning + '.png'))

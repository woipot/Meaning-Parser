import os
import json

from os import path
from wordcloud import WordCloud


def generateImgs(filename, pref):
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    text = open(path.join(d, filename)).read()
    meanings = json.loads(text)
    for key, value in meanings.items():
        generate(key, value, pref)


def generate(meaning, data, pref):
    wordcloud = WordCloud().generate_from_frequencies(data)
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    wordcloud.to_file(path.join(d, 'img/' + pref + meaning + '.png'))

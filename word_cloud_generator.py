import os
import json

from os import path
from wordcloud import WordCloud


def generateImgs():
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    text = open(path.join(d, 'last_def_set.json')).read()
    meanings = json.loads(text)
    for key, value in meanings.items():
        generate(key, value)


def generate(meaning, data):
    wordcloud = WordCloud().generate_from_frequencies(data)
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    wordcloud.to_file(path.join(d, 'img/last_'+meaning + '.png'))


import json
import logging

from articleparser import ArticleParser
from word_cloud_generator import generateImgs
# from pikabu_parser import Pikabu_Parser
# from nltk.tokenize import sent_tokenize, word_tokenize
logging.basicConfig(format=u'[%(asctime)s] # %(levelname)-8s [%(filename)s] %(message)s',
                    filename="web_parser.log", level=logging.INFO)


def readBaseDataSetFromFile(path):
    with open(path, encoding='UTF8') as json_file:
        data = json.load(json_file)

    return data


if __name__ == "__main__":
    # from nltk.tokenize import sent_tokenize # разбивает на предложения

    # logging.info('Program started')
    # article_parser = ArticleParser("mongodb://aqulasoft:aqulasoft1@185.246.152.112/daryana")

    # article_parser.createDefaultSet(readBaseDataSetFromFile("meanings.json"))

    # article_parser.selfTeaching(2000, 200)

    generateImgs("last_def_set.json", "last_")
    generateImgs("first_def_set.json", "first_")

    # pikabu_urls = [
    #     "https://pikabu.ru/tag/iphone",
    #     "https://pikabu.ru/tag/apple",
    #     "https://pikabu.ru/tag/ios",
    #     "https://pikabu.ru/tag/macos",
    #     "https://pikabu.ru/tag/macbook",
    #     "https://pikabu.ru/tag/mac",
    #     "https://pikabu.ru/tag/imac",
    #     "https://pikabu.ru/tag/ipad",
    #     "https://pikabu.ru/tag/Стив%20Джобс",
    #     "https://pikabu.ru/tag/airpods",
    # ]

    # parser = Pikabu_Parser(pikabu_urls)
    # parser.get_webdriver(path_to_webdriver_binary='/usr/local/bin/chromedriver', is_headless=False)
    # parser.get_db_collection()
    # parser.start_parse()

    # logging.info('Program finished\n')

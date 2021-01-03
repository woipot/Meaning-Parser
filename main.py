import json
import logging
import time

from articleparser import ArticleParser

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
    article_parser = ArticleParser()


    # article_parser.createDefaultSet(readBaseDataSetFromFile("meanings.json"))

    timing = time.time()
    fitedList = article_parser.fitToDefaultSet(2000)
    print(f"\nNew DEF set ready")
    for i in fitedList:
        print(f"{i} : {len(fitedList[i])}")
    print(f"\nEND time elapsed - {time.time() - timing}")


    article_parser.createDefaultSet(fitedList)


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

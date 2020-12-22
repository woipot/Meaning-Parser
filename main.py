import logging
import json
from pikabu_parser import Pikabu_Parser
from dzen_parser import Dzen_Parser

logging.basicConfig(format=u'[%(asctime)s] # %(levelname)-8s [%(filename)s] %(message)s',
                    filename="web_parser.log", level=logging.INFO)


def get_from_file(filename: str = 'pikabu_stories.txt'):

    with open(filename, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()

            if not line:
                break

            yield json.loads(line)


# pprint(list(get_from_file()))
if __name__ == "__main__":
    logging.info('Program started')

    pikabu_urls = [
        "https://pikabu.ru/tag/политика",
    ]

    dzen_urls = [
        # "https://zen.yandex.ru/t/apple",
        # "https://zen.yandex.ru/t/iphone",
        # "https://zen.yandex.ru/t/ios",
        # "https://zen.yandex.ru/t/applemusic",
        # "https://zen.yandex.ru/t/macbook",
        "https://zen.yandex.ru/t/ipad",
        "https://zen.yandex.ru/t/mac",
        "https://zen.yandex.ru/t/airpods",
        "https://zen.yandex.ru/t/macos",
        "https://zen.yandex.ru/t/faceid",
        "https://zen.yandex.ru/t/lightning",
        "https://zen.yandex.ru/appleinsider.ru",
    ]

    # parser = Pikabu_Parser(pikabu_urls)
    # parser.get_webdriver(path_to_webdriver_binary='yandexdriver.exe', is_headless=False)
    # parser.get_db_collection()
    # parser.start_parse()

    parser = Dzen_Parser(dzen_urls, 5, 100)
    parser.get_webdriver(path_to_webdriver_binary='yandexdriver.exe', is_headless=False)
    parser.get_db_collection()
    parser.start_parse()

    logging.info('Program finished\n')



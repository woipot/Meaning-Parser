import logging
import json
from pikabu_parser import Pikabu_Parser

logging.basicConfig(format=u'[%(asctime)s] # %(levelname)-8s [%(filename)s] %(message)s',
                    filename="web_parser.log", level=logging.INFO)


def get_from_file(filename: str = 'pikabu_stories.txt'):

    with open(filename, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()

            if not line:
                break

            yield json.loads(line)


if __name__ == "__main__":
    logging.info('Program started')

    pikabu_urls = [
        "https://pikabu.ru/tag/iphone",
        "https://pikabu.ru/tag/apple",
        "https://pikabu.ru/tag/ios",
        "https://pikabu.ru/tag/macos",
        "https://pikabu.ru/tag/macbook",
        "https://pikabu.ru/tag/mac",
        "https://pikabu.ru/tag/imac",
        "https://pikabu.ru/tag/ipad",
        "https://pikabu.ru/tag/Стив%20Джобс",
        "https://pikabu.ru/tag/airpods",
    ]

    parser = Pikabu_Parser(pikabu_urls)
    parser.get_webdriver(path_to_webdriver_binary='/usr/local/bin/chromedriver', is_headless=False)
    parser.get_db_collection()
    parser.start_parse()

    logging.info('Program finished\n')

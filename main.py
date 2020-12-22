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
        "https://pikabu.ru/tag/стрит%20арт",
    ]

    dzen_urls = [
        "https://zen.yandex.ru/t/космос",
    ]

    # parser = Pikabu_Parser(pikabu_urls)
    # parser.get_webdriver(path_to_webdriver_binary='yandexdriver.exe', is_headless=True)
    # parser.get_db_collection()
    # parser.start_parse()
    # # В среднем на 1 пост Пикабу было потрачено 0.8 секунды

    parser = Dzen_Parser(dzen_urls, 5, 100, 20)
    parser.get_webdriver(
        path_to_webdriver_binary='yandexdriver.exe', is_headless=False)
    parser.get_db_collection()
    parser.start_parse()
    # В среднем на 1 пост Яндекс-Дзена было потрачено 3 секунды

    logging.info('Program finished\n')


# TODO: При объединении данных в одну БД надо будет отсекать записи, где нет контента (это были записи с картинками или видео)

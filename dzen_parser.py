import html
import logging
import re
import time

from bs4 import BeautifulSoup
from pymongo import MongoClient, errors
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class Dzen_Parser:
    def __init__(self, urls, block_size: int, article_min_size: int, work_limit: int = 0):
        super().__init__(urls)
        self.block_size = block_size
        self.article_min_size = article_min_size
        self.work_limit = work_limit

    def get_webdriver(self, is_headless: bool = True):

        options = webdriver.ChromeOptions()

        if is_headless:  # для открытия браузера без открытия окна
            options.add_argument('headless')

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)

    def get_db_collection(self):
        client = MongoClient("mongodb://woipot:woipot@185.246.152.112/daryana")
        self.client = client
        db = client.web_parser
        self.db_collection = db.dzen

    def start_parse(self):
        for url in self.urls:
            self.__get_content__(html.unescape(url))

        # for url in self.stories_urls:
        #     self.driver.get(url)
        #     requiredHtml = self.driver.page_source
        #     self.__parse_story__(requiredHtml, url)

        self.driver.quit()
        self.client.close()

    def __get_content__(self, url):
        logging.info(url)
        self.driver.get(url)

        SCROLL_PAUSE_TIME = 2

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[0])
        # Get scroll height
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        i = 0
        urls_saved_while_work = 0
        parsed_stories = []
        unparsed_urls = set()
        parsed_urls = set()
        while True:
            # while i < 2:
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")

            if new_height == last_height:
                logging.info(f'end of url')
                break
            last_height = new_height
            i += 1
            logging.info(f'Iterations made: {i}')

            # Получение HTML-содержимого
            requiredHtml = self.driver.page_source
            newUrls = self.__get_urls__(requiredHtml)
            unparsed_urls |= newUrls

            unikal = unparsed_urls - parsed_urls
            if len(unikal) > self.block_size:
                self.driver.switch_to.window(self.driver.window_handles[1])
                for page_url in unikal:
                    self.driver.get(page_url)

                    parsed_story_content = self.__parse_story__(self.driver.page_source)
                    if parsed_story_content is not None:
                        parsed_stories.append(dict(_id=page_url, content=parsed_story_content))

                self.driver.switch_to.window(self.driver.window_handles[0])
                parsed_urls |= unparsed_urls
                unparsed_urls = set()

                if len(parsed_stories) > self.block_size > 0:
                    self.__save_group_to_bd__(parsed_stories)
                    urls_saved_while_work += len(parsed_stories)
                    parsed_stories = []

            if urls_saved_while_work > self.work_limit > 0:
                logging.info(f'limit has reached : {urls_saved_while_work}')
                break

        logging.info(f'Total iterations made: {i}')

    def __get_urls__(self, requiredHtml):
        soup = BeautifulSoup(requiredHtml, 'html5lib')

        g_data = soup.find_all(
            "a", {"class": "card-image-view-by-metrics__clickable"})
        logging.info(f'Stories found: {len(g_data)}')

        stories_urls = set()
        for item in g_data:
            url = item.get('href')
            stories_urls.add(url)

        return stories_urls

    def __parse_story__(self, requiredHtml):

        soup = BeautifulSoup(requiredHtml, 'html5lib')

        g_data = soup.find_all(
            "div", {"id": "article__page-root"})

        text = []
        for item in g_data:

            contents = item.find_all("div", {"class": "article-render"})

            for content in contents:
                for p in content.find_all("p", {"class": "article-render__block article-render__block_unstyled"}):
                    block_text = re.sub(r'[\t\v\r\n\f]+', ' ', p.text)
                    if len(block_text) > 0:
                        text.append(block_text)

        story_content = " ".join(text).replace('\"', '')

        if len(story_content) > self.article_min_size:
            return story_content
            # self.__load_to_file__(
            #     story=story, filename='dzen_stories.txt')
        return None

    # def __load_to_db__(self, story: dict) -> None:
    #     try:
    #         self.db_collection.insert_one(story)
    #         logging.info(f'Stories in DB: {self.db_collection.count()}')
    #     except errors.DuplicateKeyError:
    #         return

    def __save_group_to_bd__(self, parsed_stories):
        db_count = self.db_collection.count()
        duplicates_count = 0
        logging.info(f'Ready to save block: {len(parsed_stories)}')
        for story in parsed_stories:
            try:
                self.db_collection.insert_one(story)
            except errors.DuplicateKeyError:
                duplicates_count += 1

        logging.info(
            f'Stories in DB: {db_count} + {len(parsed_stories)} - {duplicates_count} = {self.db_collection.count()}')


if __name__ == "__main__":
    dzen_urls = [
        "https://zen.yandex.ru/t/apple",
        "https://zen.yandex.ru/t/iphone",
        "https://zen.yandex.ru/t/ios",
        "https://zen.yandex.ru/t/applemusic",
        "https://zen.yandex.ru/t/macbook",
        "https://zen.yandex.ru/t/ipad",
        "https://zen.yandex.ru/t/mac",
        "https://zen.yandex.ru/t/airpods",
        "https://zen.yandex.ru/t/macos",
        "https://zen.yandex.ru/t/faceid",
        "https://zen.yandex.ru/t/lightning",
        "https://zen.yandex.ru/appleinsider.ru",
    ]

    parser = Dzen_Parser(dzen_urls, 5, 100)
    parser.get_webdriver(is_headless=False)
    parser.get_db_collection()
    parser.start_parse()

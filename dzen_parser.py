import html
import logging
import re
import time

from bs4 import BeautifulSoup
from pymongo import MongoClient, errors
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from main_parser import Web_Parser


class Dzen_Parser(Web_Parser):
    def __init__(self, urls, block_size: int, article_min_size: int, work_limit: int = 0):
        super().__init__(urls)
        self.block_size = block_size
        self.article_min_size = article_min_size
        self.work_limit = work_limit

    def get_webdriver(self, path_to_webdriver_binary: str, is_headless: bool = True):

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
        savedUrlsCount = 0
        unparsed_urls = set()
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

            if len(unparsed_urls) > self.block_size:
                self.driver.switch_to.window(self.driver.window_handles[1])
                for page_url in unparsed_urls:
                    self.driver.get(page_url)
                    requiredHtml = self.driver.page_source
                    savedUrlsCount += self.__parse_story__(requiredHtml, page_url)
                self.driver.switch_to.window(self.driver.window_handles[0])
                logging.info(f'new savedCount: {savedUrlsCount}')
                unparsed_urls = set()

            if savedUrlsCount > self.work_limit > 0:
                logging.info(f'limit has reached')
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

    def __parse_story__(self, requiredHtml, url):

        soup = BeautifulSoup(requiredHtml, 'html5lib')

        g_data = soup.find_all(
            "div", {"id": "article__page-root"})

        savedCount = 0
        for item in g_data:

            contents = item.find_all("div", {"class": "article-render"})

            for content in contents:
                text = []
                for p in content.find_all("p", {"class": "article-render__block article-render__block_unstyled"}):
                    text.append(re.sub(r'[\t\v\r\n\f]+', ' ', p.text))

                story = dict(_id=url,
                             content=" ".join(text).replace('\"', ''))
                if len(story["content"]) > self.article_min_size:
                    self.__load_to_db__(story)
                    savedCount += 1
                    # self.__load_to_file__(
                    #     story=story, filename='dzen_stories.txt')
        return savedCount

    def __load_to_db__(self, story: dict) -> None:
        try:
            self.db_collection.insert_one(story)
            logging.info(f'Stories in DB: {self.db_collection.count()}')
        except errors.DuplicateKeyError:
            return

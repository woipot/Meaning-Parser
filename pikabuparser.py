import html
import logging
import re
import time

from bs4 import BeautifulSoup
from pymongo import MongoClient, errors
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class PikabuParser:
    def __init__(self, urls):
        self.urls = urls

    def initWebdriver(self, is_headless: bool = True):
        """

        :param is_headless: open browser window or work silent
        """
        options = webdriver.ChromeOptions()

        if is_headless:
            options.add_argument('headless')

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)

    def initDataBase(self):
        client = MongoClient("mongodb://woipot:woipot@aqulasoft.com/daryana")
        self.clinent = client
        db = client.web_parser
        self.db_collection = db.pikabu

    def startParse(self):
        """
        !IMPORTANT to correct work you need setup breakpoint and log in to pikabu account and activate endless scroll
        NOT PAGES
        """
        for url in self.urls:
            self.parseTag(html.unescape(url))

        self.driver.quit()
        self.clinent.close()

    def parseTag(self, url):
        logging.info(url)
        self.driver.get(url)

        SCROLL_PAUSE_TIME = 5

        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        i = 0
        while True:

            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(SCROLL_PAUSE_TIME)

            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height
            i += 1
            logging.info(f'Iterations made: {i}')

            requiredHtml = self.driver.page_source
            self.parseArticle(requiredHtml)

        logging.info(f'Total iterations made: {i}')

    def parseArticle(self, requiredHtml):

        soup = BeautifulSoup(requiredHtml, 'html5lib')

        g_data = soup.find_all("div", {"class": "story__main"})
        logging.info(f'Stories found: {len(g_data)}')

        for item in g_data:

            urls = item.find_all("h2", {"class": "story__title"})
            contents = item.find_all("div", {"class": "story__content-inner"})

            for (url, content) in zip(urls, contents):

                story = dict(_id=url.find('a').get('href'),
                             content=re.sub(r'[\t\v\r\n\f]+', ' ', content.text))

                if len(story["content"]) > 300:
                    self.saveToDb(story)

    def saveToDb(self, story: dict) -> None:
        try:
            self.db_collection.insert_one(story)
            logging.info(f'Stories in DB: {self.db_collection.count()}')
        except errors.DuplicateKeyError:
            return


if __name__ == "__main__":

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

    parser = PikabuParser(pikabu_urls)
    parser.initWebdriver(is_headless=False)
    parser.initDataBase()
    parser.startParse()

    logging.info('Program finished\n')

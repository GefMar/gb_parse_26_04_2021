import json
import time
import typing

import requests
from urllib.parse import urljoin
import bs4
import pymongo
from database.database import Database


class GbBlogParse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) "
        "Gecko/20100101 Firefox/88.0"
    }
    __parse_time = 0

    def __init__(self, stat_url, database: Database, delay=1.0):
        self.start_url = stat_url
        self.db = database
        self.delay = delay
        self.done_urls = set()
        self.tasks = []
        self.task_creator(self.start_url, callback=self.parse_feed)

    def _get_response(self, url):
        next_time = self.__parse_time + self.delay
        while True:
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response
            time.sleep(self.delay)

    def _get_soup(self, url):
        response = self._get_response(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def task_creator(self, *urls, callback):
        urls_set = set(urls) - self.done_urls
        for url in urls_set:
            self.tasks.append(self.get_task(url, callback))
            self.done_urls.add(url)

    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        pag_links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in ul_pagination.find_all("a")
            if itm.attrs.get("href")
        )
        self.task_creator(*pag_links, callback=self.parse_feed)
        post_links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in soup.find_all("a", attrs={"class": "post-item__title"})
            if itm.attrs.get("href")
        )
        self.task_creator(*post_links, callback=self.parse_post)

    def parse_post(self, url, soup):
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        data = {
            "post_data": {
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "url": url,
                "id": soup.find("comments").attrs.get("commentable-id"),
            },
            "author_data": {
                "url": urljoin(url, author_tag.parent.attrs.get("href")),
                "name": author_tag.text,
            },
            "tags_data": [
                {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comments(soup.find("comments").attrs.get("commentable-id")),
        }
        return data

    def _get_comments(self, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = self._get_response(urljoin(self.start_url, api_path))
        data = response.json()
        return data

    def run(self):
        while True:
            try:
                task = self.tasks.pop(0)
            except IndexError:
                break
            result = task()
            if isinstance(result, dict):
                self.save(result)

    def save(self, data):
        self.db.add_post(data)
        print(1)


if __name__ == "__main__":
    # mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    # db = mongo_client["gb_parse_26_04_2021"]
    # collection = db["gb_blog_parse"]
    db = Database("sqlite:///gb_blog.db")
    parser = GbBlogParse("https://gb.ru/posts", db, delay=0.1)
    parser.run()

import json
import time
from pathlib import Path
import requests
from urllib.parse import urlparse


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) "
        "Gecko/20100101 Firefox/88.0"
    }
    __parse_time = 0

    def __init__(self, start_url, save_path, delay=0.2):
        self.start_url = start_url
        self.save_path = save_path
        self.delay = delay

    def run(self):
        for product in self._parse(self.start_url):
            file_path = self.save_path.joinpath(f"{product['id']}.json")
            self.save(product, file_path)

    def _get_response(self, url):
        next_time = self.__parse_time + self.delay
        url = url.replace(urlparse(url).netloc, urlparse(self.start_url).netloc)
        while True:
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response
            time.sleep(self.delay)

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data.get("next")
            for product in data.get("results", []):
                yield product

    def save(self, data: dict, save_path):
        save_path.write_text(json.dumps(data, ensure_ascii=False))


class CategoriesParser(Parse5ka):
    def __init__(self, categories_url, *args, **kwargs):
        self.categories_url = categories_url
        super().__init__(*args, **kwargs)

    def _get_categories(self):
        response = self._get_response(self.categories_url)
        data = response.json()
        return data

    def run(self):
        for category in self._get_categories():
            category["products"] = []
            params = f"?categories={category['parent_group_code']}"
            url = f"{self.start_url}{params}"

            category["products"].extend(list(self._parse(url)))
            file_name = f"{category['parent_group_code']}.json"
            cat_path = self.save_path.joinpath(file_name)
            self.save(category, cat_path)


def get_save_dir(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    cat_url = "https://5ka.ru/api/v2/categories/"
    save_path_products = get_save_dir("products")
    save_path_categories = get_save_dir("categories")
    parser_products = Parse5ka(url, save_path_products)
    cat_parser = CategoriesParser(cat_url, url, save_path_categories)
    cat_parser.run()

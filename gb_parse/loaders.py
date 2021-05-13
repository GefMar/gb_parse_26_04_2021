from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


def clear_price(price):
    try:
        result = float(price.replace("\u2009", ""))
    except ValueError:
        result = None
    return result


def author_link(item):
    if item:
        item = urljoin("https://youla.ru/user/", item)
    return item


def get_characteristics(item: str) -> dict:
    selector = Selector(text=item)
    data = {}
    data["name"] = selector.xpath(
        "//div[contains(@class, 'AdvertSpecs_label')]/text()"
    ).extract_first()
    data["value"] = selector.xpath(
        "//div[contains(@class, 'AdvertSpecs_data')]//text()"
    ).extract_first()
    return data


def flat_text(items):
    return "\n".join(items)


def hh_user_url(user_id):
    return urljoin("https://hh.ru/", user_id)


class AutoyoulaLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
    author_in = MapCompose(author_link)
    author_out = TakeFirst()
    description_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)


class HHLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = flat_text
    # description_in = flat_text,
    # description_out = flat_text,
    author_in = MapCompose(hh_user_url)
    author_out = TakeFirst()

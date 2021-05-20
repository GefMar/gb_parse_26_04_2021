# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from . import settings
from pymongo import MongoClient


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class GbMongoPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client[settings.BOT_NAME]

    def process_item(self, item, spider):
        self.db[spider.name if isinstance(item, dict) else type(item).__name__].insert_one(item)
        return item


class GbImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for photo in item.get("photos", []):
            yield Request(photo)

    def item_completed(self, results, item, info):
        if item.get("photos"):
            item["photos"] = [itm[1] for itm in results]
        return item

import scrapy
from w3lib.html import remove_tags

import pymongo


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]


    def _get_follow(self, response, selector, callback):
        for link in response.css(selector):
            url = link.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response):
        yield from self._get_follow(
            response,
            "div.TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink",
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, "div.Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse,
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
            self.car_parse,
        )


    def car_parse(self, response):
        data = {
            "url": response.url,
            
            "title": response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
           
            "images": response.css(".PhotoGallery_photoImage__2mHGn").getall(),
            
            "prop": remove_tags(response.css(".AdvertCard_specs__2FEHc").get()),
            
            #"phone": response.css(".PopupPhoneNumber_number__1hybY")
            "descr" :
                response.css(".AdvertCard_descriptionInner__KnuRi::text").get(),
            
            "avtor": response.css(".SellerInfo_name__3Iz2N").get(),
        }

        yield data

        client = pymongo.MongoClient('localhost', 27017)
        self.mongo_base = client["auto"]
        collection = self.mongo_base["autoyoula"]
        collection.insert_one(data)

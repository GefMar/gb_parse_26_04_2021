import scrapy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class ZillowSpider(scrapy.Spider):
    name = "zillow"
    allowed_domains = ["www.zillow.com"]
    start_urls = ["https://www.zillow.com/san-francisco-ca/"]
    _xpaths = {
        "pagination": '//nav[@role="navigation"]/ul/li/'
        'a[contains(@class,"PaginationButton")]/@href',
        "ads": '//article[@role="presentation"]//a[contains(@class, "list-card-link")]/@href',
    }

    def __init__(self, *args, **kwargs):
        super(ZillowSpider, self).__init__(*args, **kwargs)
        self.browser = webdriver.Firefox()

    def parse(self, response):
        print(1)
        for url in response.xpath(self._xpaths["pagination"]):
            yield response.follow(url, callback=self.parse)

        for url in response.xpath(self._xpaths["ads"]):
            yield response.follow(url, callback=self.ads_parse)

    def ads_parse(self, response):
        print(1)
        self.browser.get(response.url)
        media_col = self.browser.find_element_by_xpath('//div[@data-media-col="true"]')
        len_photos = len(
            media_col.find_elements_by_xpath("//picture[contains(@class, 'media-stream-photo')]")
        )
        while True:
            for _ in range(5):
                media_col.send_keys(Keys.PAGE_DOWN)

            photos = media_col.find_elements_by_xpath(
                "//picture[contains(@class, 'media-stream-photo')]"
            )

            if len_photos == len(photos):
                break
            len_photos = len(photos)

        print(1)

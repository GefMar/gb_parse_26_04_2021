from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gbparse.spiders.autoyoula import AutoyoulaSpider



if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("gbparse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(AutoyoulaSpider)
    crawler_process.start()

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from goodsparser.spiders.amag import AmagSpider
from goodsparser import settings

search = "полироль"

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # search = input('')
    process.crawl(AmagSpider, search=search)
    process.start()

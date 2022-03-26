from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    # process2 = CrawlerProcess(settings=crawler_settings)
    # process2.crawl(SjruSpider)
    # process2.start()
    #
    # process1 = CrawlerProcess(settings=crawler_settings)
    # process1.crawl(HhruSpider)
    # process1.start()

    #doesn`t work
    # raise error.ReactorAlreadyInstalledError("reactor already installed")
    # twisted.internet.error.ReactorAlreadyInstalledError: reactor already installed
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)
    process.crawl(SjruSpider)
    process.start()

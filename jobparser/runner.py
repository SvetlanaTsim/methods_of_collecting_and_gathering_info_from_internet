# from scrapy.crawler import CrawlerProcess
# from scrapy.settings import Settings
# from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

if __name__ == '__main__':

    #doesn`t work, raises twisted.internet.error.ReactorAlreadyInstalledError
    # raise error.ReactorAlreadyInstalledError("reactor already installed")
    # twisted.internet.error.ReactorAlreadyInstalledError: reactor already installed

    # crawler_settings = Settings()
    # crawler_settings.setmodule(settings)
    # process = CrawlerProcess(settings=crawler_settings)
    # process.crawl(HhruSpider)
    # process.crawl(SjruSpider)
    # process.start()

    #works
    configure_logging()
    settings = get_project_settings()  # settings not required if running
    runner = CrawlerRunner(settings)  # from script, defaults provided
    runner.crawl(HhruSpider)  # your loop would go here
    runner.crawl(SjruSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # the script will block here until all crawling jobs are finished

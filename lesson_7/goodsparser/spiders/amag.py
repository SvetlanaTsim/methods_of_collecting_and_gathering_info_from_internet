import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from goodsparser.items import GoodsparserItem

class AmagSpider(scrapy.Spider):
    name = 'amag'
    allowed_domains = ['amag.ru']
    def __init__(self, search, **kwargs):
        super().__init__(**kwargs)
        self.search = search
        self.start_urls = [f'https://www.amag.ru/search/?q={self.search}']

    def parse(self, response):
        next_page = response.xpath('//ul[@class="pagination"]/li[last()]/a/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@class="prodLinkBlock"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=GoodsparserItem(), response=response)
        loader.add_xpath('name', "//h1[@class='name']/text()")
        loader.add_xpath('price', "//div[@class='total_price']/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('photos', "//div[@class='loupe']/img/@src | //div[@class='dt-gallery-bottom hidden-xs']/ul/li/a/img/@src")
        yield loader.load_item()

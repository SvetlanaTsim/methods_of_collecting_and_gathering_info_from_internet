import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Br%5D%5B0%5D=3',
                  'https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@class="icMQ_ bs_sM _3ze9n _2iGzu f-test-button-dalshe f-test-link-Dalshe"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[contains(@class,"icMQ_ _6AfZ9")]/@href').getall()
        for link in links:
            yield response.follow(('https://www.superjob.ru' + link), callback=self.vacancy_parse_sj)

    def vacancy_parse_sj(self, response: HtmlResponse):
        name = response.xpath('//h1[@class="_3AWCp _2KQmo _3id6r _1wB_Y _35kb8 _26ig7 _1d47O"]//text()').get()
        salary = response.xpath("//span[@class='_2Wp8I _1BiPY _26ig7 _18w_0']//text()").getall()
        link = response.url
        item = JobparserItem(name=name, salary=salary, link=link)
        yield item

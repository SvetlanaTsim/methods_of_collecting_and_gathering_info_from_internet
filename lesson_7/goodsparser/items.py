# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from itemloaders.processors import MapCompose, TakeFirst
import scrapy


def clear_price(value):
    value = value.replace('\xa0', '').replace('\n\t\t\t\t\t\t\t\t\t\t\t\t', '')
    try:
        return int(value)
    except:
        return value


class GoodsparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(clear_price))
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(clear_price))
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    _id = scrapy.Field()


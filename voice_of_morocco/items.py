import scrapy

class JaridaItem(scrapy.Item):
    idPost = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    text = scrapy.Field()
    images = scrapy.Field()
    videos = scrapy.Field()
    links = scrapy.Field()
    url = scrapy.Field()

import scrapy

class JaridaItem(scrapy.Item):
    # Unique post id (from URL slug when available)
    idPost = scrapy.Field()
    # Article title
    title = scrapy.Field()
    # ISO date string (YYYY-MM-DD) or datetime/date object
    date = scrapy.Field()
    # Main article text (string)
    text = scrapy.Field()
    # List of image URLs
    images = scrapy.Field()
    # List of video URLs or embed src values
    videos = scrapy.Field()
    # List of links found in the article
    links = scrapy.Field()
    # Canonical URL of the article
    url = scrapy.Field()

# Optional: a simpler item used by other spiders (keeps backward compatibility)
class VoiceItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    images = scrapy.Field()
    links = scrapy.Field()

__all__ = ["JaridaItem", "VoiceItem"]

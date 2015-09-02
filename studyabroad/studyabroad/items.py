# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Post(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    tag = scrapy.Field()
    total_push = scrapy.Field()
    mark = scrapy.Field()
    raw = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    published = scrapy.Field()
    comments = scrapy.Field()
    ip = scrapy.Field()

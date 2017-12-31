# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ZhilianScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    job_name = scrapy.Field()
    company = scrapy.Field()
    address = scrapy.Field()
    job_info = scrapy.Field()
    job_tags = scrapy.Field()
    salary = scrapy.Field()
    job_link = scrapy.Field()


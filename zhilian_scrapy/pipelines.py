# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class ZhilianScrapyPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost",connect=False)
        db = client["zhilian"]
        self.collection = db["python"]

    def process_item(self, item, spider):
        content = dict(item)
        self.collection.insert(content)
        print("###################已经存入MongoDB########################")
        return item

    def close_spider(self,spider):
        pass


# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class SuningBookSpiderPipeline(object):
    def __init__(self):
        self.mongo_client = MongoClient()

    def process_item(self, item, spider):
        spider.col.insert(item)
        return item

    def open_spider(self,spider):
        if spider.name == 'suning_book':
            spider.col = self.mongo_client['suning']['book']

    def close_spider(self,spider):
        pass

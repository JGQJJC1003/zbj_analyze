# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyZbjItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    item_title = scrapy.Field()
    link_name = scrapy.Field()
    company_icon = scrapy.Field()
    company_address = scrapy.Field()
    company_level = scrapy.Field()
    company_name = scrapy.Field()
    company_link = scrapy.Field()
    company_type = scrapy.Field()
    company_deposit = scrapy.Field()
    serviced_employer = scrapy.Field()
    head_turn = scrapy.Field()
    good_rate = scrapy.Field()
    company_id = scrapy.Field()
    impression_tips = scrapy.Field()
    ability_number1 = scrapy.Field()
    ability_number2 = scrapy.Field()
    ability_number3 = scrapy.Field()
    company_income = scrapy.Field()

# -*- coding: utf-8 -*-
import scrapy
import json
import time
import scrapy
from scrapy_redis.spiders import RedisSpider

from scrapy_zbj.items import ScrapyZbjItem


class ZbjSpider(RedisSpider):
    name = 'zbj'
    allowed_domains = []
    # start_urls = ['https://zhengzhou.zbj.com/?pmcode=116578316&utm_source=bdpz&utm_medium=SEM']
    redis_key = 'zbj:start_urls'

    # 解析主页所有的分类标签，抛给company_list_parse解析。
    def parse(self, response):
        item_list = response.xpath('//div[@class="cate-info-item"]')
        for item in item_list:
            item_title = item.xpath('.//div[@class="item-title "]/a/text()')[0].extract()
            item_links = item.xpath('.//div[@class="item-link hover-anima"]')
            for item_link in item_links:
                link_name = item_link.xpath('./a/text()')[0].extract()

                link_href = item_link.xpath('./a/@href')[0].extract()
                time.sleep(10)
                yield scrapy.Request(url=link_href, callback=self.company_list_parse,
                                     meta={'item_title': item_title, 'link_name': link_name})

        # 解析公司展示页面，抓取该页面的每一条公司的信息，把impression_api接口抛出，带着item,把下一页的url抛出

    def company_list_parse(self, response):
        item = ScrapyZbjItem()
        item_title = response.meta['item_title']
        link_name = response.meta['link_name']

        company_list = response.xpath('//div[@class="item-wrap j-sp-item-wrap"]')
        for company in company_list:
            company_icon = 'http:' + company.xpath(
                './/div[@class="witkey-info"]//div[@class="witkey-avatar"]//img[@class="lazy"]/@data-original')[
                0].extract()
            try:
                company_address = \
                company.xpath('.//div[@class="clearfix witkey-hd"]//span[@class="ico city-icon"]//span/text()')[
                    0].extract()
            except Exception:
                print('地址获取失败，当前页url:{}'.format(response.url))
                company_address = '未知'
            try:
                company_level = \
                company.xpath('.//div[@class="clearfix witkey-hd"]//span[contains(@class,"ico-level")]/text()')[
                    0].extract()
            except Exception:
                print('等级获取失败，当前页url:{}'.format(response.url))
                company_level = '天蓬网'
            company_name = company.xpath('.//a[@class="name"]/text()')[0].extract().strip()
            company_link = 'http:' + company.xpath('.//a[@class="name"]/@href')[0].extract()

            try:
                company_type = \
                company.xpath('.//div[@class="clearfix witkey-hd"]//span[@class=" ico ico-user-business"]/text()')[
                    0].extract()
            except Exception:
                company_type = '个人'

            try:
                company_deposit = company.xpath(
                    './/div[@class="clearfix witkey-hd"]//span[@class="j-bz-wrap bz-wrap"]//span[@class="ico bz-border"]/text()')[
                    0].extract()
            except Exception:
                company_deposit = '0'

            serviced_employer = company.xpath('.//div[@class="witkey-dync"]//span[1]/text()')[0].extract()[6:-1]
            head_turn = company.xpath('.//div[@class="witkey-dync"]//span[2]/text()')[0].extract()[6:-3]
            good_rate = company.xpath('.//div[@class="witkey-dync"]//span[@class="user-impression"]//i/text()')[
                            0].extract()[:-1]
            company_id = company.xpath('./@data-shop-id')[0].extract()

            item['item_title'] = item_title
            item['link_name'] = link_name
            item['company_icon'] = company_icon
            item['company_address'] = company_address
            item['company_level'] = company_level
            item['company_name'] = company_name
            item['company_link'] = company_link
            item['company_type'] = company_type
            item['company_deposit'] = company_deposit
            item['serviced_employer'] = serviced_employer
            item['head_turn'] = head_turn
            item['good_rate'] = good_rate
            item['company_id'] = company_id

            item_dict = {
                'item': item
            }
            impression_api = 'https://zhengzhou.zbj.com/s/api/queryImpressionTopById?userId={}'.format(company_id)

            yield scrapy.Request(url=impression_api, callback=self.impression_parse, meta=item_dict)

        try:
            next_page = response.xpath('//div[@class="pagination"]//a[@class="pagination-next"]/@href')[0].extract()
        except Exception:
            print('下一页获取失败，当前url:{}'.format(response.url))
            next_page = 'avascript:;'

        if next_page != 'javascript:;':
            next_page = 'https://zhengzhou.zbj.com' + next_page
            yield scrapy.Request(url=next_page, callback=self.company_list_parse,
                                 meta={'item_title': item_title, 'link_name': link_name})

        # 获取impression_tips的接口数据，然后取出item的company_link抛出给抓取交易详情页的数据

    def impression_parse(self, response):
        item = response.meta['item']
        impression_json = json.loads(response.text)
        impression_tips = ''
        if impression_json['data']['data'] == []:
            impression_tips = '无'
        else:
            for i in impression_json['data']['data']:
                impression_tips += str(i['num']) + ',' + i['name'] + '.'
        item['impression_tips'] = impression_tips
        company_link = item['company_link']
        yield scrapy.Request(url=company_link, callback=self.company_main_parse, meta={'item': item})

        # 解析主页，
        # 两种页面，一种是直接就在主页能找到交易详情信息
        # 另一种页面，一种是直接就在主页能找到交易详情信息

    def company_main_parse(self, response):
        item = response.meta['item']
        try:
            # 能找到nav_ul则是交易次数较多的页面
            nav_ul = response.xpath('//ul[@class="witkeyhome-nav clearfix"]')[0].extract()
            ability_number1 = response.xpath('//div[@class="shop-evaluate-det"]//span/text()')[0].extract()
            ability_number2 = response.xpath('//div[@class="shop-evaluate-det"]//span/text()')[2].extract()
            ability_number3 = response.xpath('//div[@class="shop-evaluate-det"]//span/text()')[4].extract()
            company_income = response.xpath('//div[@class="personal-shop-balance"]/span[1]/text()')[
                0].extract().replace(',', '')
            item['ability_number1'] = ability_number1
            item['ability_number2'] = ability_number2
            item['ability_number3'] = ability_number3
            item['company_income'] = company_income
            yield item
        except Exception as e:

            company_income = \
            response.xpath('//ul[@class="ability-wrap clearfix"]/li[2]/div[@class="ability-content"]/text()')[
                0].extract().strip()
            ability_number1 = \
            response.xpath('//div[@class="ability-content"]//span[contains(@class,"ability-number")]/text()')[
                0].extract()
            ability_number2 = \
            response.xpath('//div[@class="ability-content"]//span[contains(@class,"ability-number")]/text()')[
                1].extract()
            ability_number3 = \
            response.xpath('//div[@class="ability-content"]//span[contains(@class,"ability-number")]/text()')[
                2].extract()
            item['ability_number1'] = ability_number1
            item['ability_number2'] = ability_number2
            item['ability_number3'] = ability_number3
            item['company_income'] = company_income

            yield item
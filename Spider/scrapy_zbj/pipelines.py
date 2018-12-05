# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class ScrapyZbjPipeline(object):
    def open_spider(self,spider):
        self.db = pymysql.connect(host='10.8.157.39', port=3306, user='root', password='123456',database='zbj',charset='utf8')

    # 关闭链接
    def close_spider(self,spider):
        self.db.close()

    def process_item(self, item, spider):
        self.save_to_mysql(item)

        return item

    # 保存至数据库
    def save_to_mysql(self, item):
        cursor = self.db.cursor()
        # sql = """insert into company(company_name,company_address,company_level,company_icon,company_link,company_type,company_deposit,serviced_employer,head_turn,good_rate,impression_tips,company_income,item_title,link_name,company_id,ability_number1,ability_number2,ability_number3) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        sql = 'insert into company(company_name,company_address,company_level,company_icon,company_link,company_type,company_deposit,serviced_employer,head_turn,good_rate,impression_tips,company_income,item_title,link_name,company_id,ability_number1,ability_number2,ability_number3) values ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'
        sql = sql.format(item['company_name'],item['company_address'],item['company_level'],item['company_icon'],item['company_link'],item['company_type'],item['company_deposit'],item['serviced_employer'],item['head_turn'],item['good_rate'],item['impression_tips'],item['company_income'],item['item_title'],item['link_name'],item['company_id'],item['ability_number1'],item['ability_number2'],item['ability_number3'])


        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print('*'*50)
            print(e)
            self.db.rollback()

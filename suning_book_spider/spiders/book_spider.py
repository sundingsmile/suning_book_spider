# -*- coding: utf-8 -*-
import scrapy
import re

class TestSpider(scrapy.Spider):
    name = 'suning_book'
    allowed_domains = ['list.suning.com','product.suning.com']
    start_urls = ['https://book.suning.com/']

    # 提取分类URL
    def parse(self, response):
        book_class_list = response.xpath('//div[@class="submenu-left"]/ul/li')
        print('一共有{}种分类'.format(len(book_class_list)))
        for temp in book_class_list:
            book_class_url = temp.xpath('./a/@href').extract_first()
            # print(book_class_url)
            yield scrapy.Request(book_class_url,callback=self.parse_class_url)

    # 提取书的详细URL信息
    def parse_class_url(self,response):
        print('*' * 100)
        print(response.url)
        book_list = response.css('#filter-results li')
        print('每一页有{}本书'.format(len(book_list)))
        for temp in book_list:
            book_url= 'https:' + temp.css('.res-info a::attr(href)').extract_first()
            yield scrapy.Request(book_url,callback=self.parse_book_info)

        # 获取总页数
        if re.findall('共(\d+)页，到第',response.text) == []:
            # print('-' * 100)
            if response.xpath('//a[@id="nextPage"]/preceding-sibling::a[1]/text()').extract_first():
                page_num = int(response.xpath('//a[@id="nextPage"]/preceding-sibling::a[1]/text()').extract_first())
            else:
                page_num = 0
        else:
            page_num = int(re.findall('共(\d+)页，到第',response.text)[0])

        # 翻译地址模板
        next_url_temp1 = 'https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp={}&il=0&iy=0&adNumber=0&n=1&ch=4&prune=0&sesab=ACBAABC&id=IDENTIFYING&cc=311'
        next_url_temp2 = 'https://search.suning.com/emall/searchProductList.do?keyword={}&ci=0&pg=01&cp={}&il=1&st=0&iy=0&adNumber=0&n=1&ch=4&sesab=ACAABAABCAAA&id=IDENTIFYING&cc=311'
        # 获取书的分类id
        book_class_id = re.findall('"categoryId": "(\d)+",',response.text)[0]

        print('总页数{}'.format(page_num))
        # 翻页
        for i in range(1,page_num + 1,1):
            # print('-' * 100)
            # print('总页数{}'.format(page_num))
            # print('这是第{}页'.format(i))
            # print('-' * 100)
            if response.css('#nextPage'):
                next_page_url = next_url_temp1.format(book_class_id,i)
                yield scrapy.Request(
                    next_page_url,
                    callback=self.parse_next_page
                )
            else:
                next_page_url = next_url_temp2.format(book_class_id,i)
                yield scrapy.Request(
                    next_page_url,
                    callback=self.parse_next_page
                )

    # 获取下一页中书的详细信息
    def parse_next_page(self,response):
        print('提取数据中')
        book_list = response.css('#filter-results li')
        for temp in book_list:
            book_url = 'https:' + temp.css('.res-info a::attr(href)').extract_first()
            yield scrapy.Request(book_url, callback=self.parse_book_info)


    # 提取书的详细信息
    def parse_book_info(self,response):
        # print('提取详细信息中')
        items = {}
        items['book_info'] = re.sub('\s','',response.xpath('//h1[@id="itemDisplayName"]/text()').extract_first())
        items['book_price'] = re.findall('"itemPrice":"(.*?)"',response.text)[0]
        items['book_author'] = re.sub('\s','',response.css('#proinfoMain li:nth-child(1)::text').extract_first())
        try:
            items['book_publisher'] = re.sub('\s','',response.css('#proinfoMain li:nth-child(2)::text').extract_first())
        except:
            items['book_publisher'] = ''
        try:
            items['book_publish_time'] = re.sub('\s','',response.css('#proinfoMain  li:nth-child(3) span:nth-child(2)::text').extract_first())
        except Exception as e:
            items['book_publish_time'] = ''
        # print(items)
        yield items
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
        # 获取总页数
        if re.findall('共(\d+)页，到第',response.text) == []:
            # print('-' * 100)
            if response.xpath('//a[@id="nextPage"]/preceding-sibling::a[1]/text()').extract_first():
                page_num = int(response.xpath('//a[@id="nextPage"]/preceding-sibling::a[1]/text()').extract_first())
            else:
                page_num = 0
        else:
            page_num = int(re.findall('共(\d+)页，到第',response.text)[0])

        # 翻页地址模板
        if response.url.find('keyword') == -1:
            book_list_front_half = 'https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp={}&il=0&iy=0&adNumber=0&n=1&ch=4&prune=0&sesab=ACBAABC&id=IDENTIFYING&cc=010'
            book_list_back_half = 'https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp={}&il=0&iy=0&adNumber=0&n=1&ch=4&prune=0&sesab=ACBAABC&id=IDENTIFYING&cc=010&paging=1&sub=0'
        else:
            book_list_front_half = 'https://search.suning.com/emall/searchProductList.do?keyword={}&ci=0&pg=01&cp={}&il=1&st=0&iy=0&adNumber=0&n=1&ch=4&sesab=ACAABAABCAAA&id=IDENTIFYING&cc=010'
            book_list_back_half = 'https://search.suning.com/emall/searchProductList.do?keyword={}&ci=0&pg=01&cp={}&il=1&st=0&iy=0&adNumber=0&n=1&ch=4&sesab=ACAABAABCCAA&id=IDENTIFYING&cc=010&paging=1&sub= 0'
        # 获取书的分类id
        book_class_id = re.findall('"categoryId": "(\d+)",',response.text)[0]
        print('*' * 100)
        print(response.url)
        print('总页数{}'.format(page_num))
        print('书类ID为{}'.format(book_class_id))

        # 翻页
        for i in range(0,page_num + 1,1):
            # print('翻页中')
            next_page_fron_url = book_list_front_half.format(book_class_id,i)
            # print('nextPage', i)
            # print(next_page_fron_url)
            yield scrapy.Request(
                next_page_fron_url,
                callback=self.parse_book_url
            )
            next_page_back_url = book_list_back_half.format(book_class_id,i)
            # print('nextPage', i)
            # print(next_page_back_url)
            yield scrapy.Request(
                next_page_back_url,
                callback=self.parse_book_url
            )

    # 获取下一页中书的详细信息
    def parse_book_url(self,response):
        if response.url.find('paging') != -1:
            book_list = response.css('li')
            if len(book_list) == 0:
                print('-' * 100)
                print('URL：',response.url)
            for temp in book_list:
                book_url = 'https:' + temp.css('.res-info a::attr(href)').extract_first()
                # print('-' * 100)
                # print('book_url:',book_url)
                yield scrapy.Request(book_url, callback=self.parse_book_info)
        else:
            book_list = response.css('#filter-results li')
            if len(book_list) == 0:
                print('#' * 100)
                print('URL：',response.url)
            for temp in book_list:
                book_url = 'https:' + temp.css('.res-info a::attr(href)').extract_first()
                # print('-' * 100)
                # print('book_url:',book_url)
                yield scrapy.Request(book_url, callback=self.parse_book_info)


    # 提取书的详细信息
    def parse_book_info(self,response):
        items = {}
        try:
            items['book_info'] = re.sub('\s','',response.xpath('//h1[@id="itemDisplayName"]/text()').extract()[1])
        except:
            items['book_info'] = ''
        try:
            items['book_price'] = re.findall('"itemPrice":"(.*?)"',response.text)[0]
        except:
            items['book_price'] = 'No price for now'
        items['book_author'] = re.sub('\s','',response.css('#proinfoMain li:nth-child(1)::text').extract_first())
        try:
            items['book_publisher'] = re.sub('\s','',response.css('#proinfoMain li:nth-child(2)::text').extract_first())
        except:
            items['book_publisher'] = ''
        try:
            items['book_publish_time'] = re.sub('\s','',response.css('#proinfoMain  li:nth-child(3) span:nth-child(2)::text').extract_first())
        except Exception as e:
            items['book_publish_time'] = ''
        print(items)
        yield items
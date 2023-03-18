import json

import scrapy
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib.parse import urljoin


class mySpider(scrapy.Spider):

    name = "zzrsb"
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m-%d")
        template = "http://www.zuzhirenshi.com/dianzibao/{date}/1/index.htm"
        for d in dates:
            yield FormRequest(template.format(date = d),dont_filter = True)


    def parse(self, response, **kwargs):
        # print(response.text)
        # next_urls = re.findall('../../../dianzibao/\d+-\d+-\d+/\d+/index.htm', response.text)
        next_pages_str = re.findall('var SubLanMuList = \[(\{.+})];', response.text)[0]
        next_pages = re.findall('\{"lmmc":".+?",.*?"lmid":\d+}', next_pages_str)
        # print(next_pages)
        for i, page in enumerate(next_pages):
            url_next = response.url.replace('1/index', '%s/index' % i)
            print(url_next)
            yield FormRequest(url_next, callback=self.parse_page)

    def parse_page(self, response, **kwargs):
        # next_urls = re.findall('../../../dianzibao/\d+-\d+-\d+/\d+/[0-9a-z\-]+.htm', response.text)
        next_urls = re.findall('"infoid":"([0-9a-z\-]+?)","id":', response.text)
        # print(next_urls)
        for infoid in next_urls:
            # href = url.replace('../', '')
            url_next = response.url.replace('index', infoid)
            yield FormRequest(url_next, callback=self.parse_item)

    def parse_item(self, response):
        title = response.xpath('//div[@class="innertop"]//text()').extract()
        content = response.xpath('//div[@class="innercontent"]//text()').extract()
        date = response.xpath('//div[@class="innertop"]/text()').extract()
        url = response.url
        imgs = response.xpath('//div[@class="innercontent"]//@src').extract()

        item = NewscrapyItem()
        item['title'] = re.sub('[\n\r\s\t]', '', ','.join(title))
        item['content'] = re.sub('[\n\r\s\t]', '', ','.join(content))
        item['date'] = re.sub('[\n\r\s\t]', '', ','.join(date))
        item['url'] = url
        item['newspaper'] = self.name
        item['imgs'] = imgs
        yield item

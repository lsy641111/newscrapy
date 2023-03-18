import scrapy
from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse
from urllib.parse import urljoin

import json



class mySpider(scrapy.Spider):

    name = "zgsyb"
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "http://app.zgsyb.com.cn/paper/layout/{date}/l01.html"
        for d in dates:
            yield FormRequest(template.format(date = d),dont_filter = True)

    def parse(self, response, **kwargs):
        next_urls = re.findall('l\d+.html', response.text)
        for url in next_urls:
            url_next = f'http://app.zgsyb.com.cn/paper/layout/202208/26/{url}'
            yield FormRequest(url_next, callback=self.parse_page)
    def parse_page(self, response, **kwargs):
        next_urls = re.findall('c/\d+/\d+/c\d+.html', response.text)
        # print(next_urls)
        for url in next_urls:
            url_next = f'http://app.zgsyb.com.cn/paper/{url}'
            yield FormRequest(url_next, callback=self.parse_item)

    def parse_item(self, response):
        title = response.xpath('//h2[@id="Title"]//text()').extract()
        content = response.xpath('//div[@id="ozoom"]//text()').extract()
        url = response.url
        date = re.search("c/(\d+/\d+)/c", url).group(1)
        date = '-'.join([date[0:4], date[4:6], date[7:9]])
        imgs = response.xpath(".//div[@class='attachment']//@src").extract()
        imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
        

        item = NewscrapyItem()
        item['title'] = re.sub('[\n\r\s\t]', '', ','.join(title))
        item['content'] = re.sub('[\n\r\s\t]', '', ','.join(content))
        item['date'] = date
        item['url'] = url
        item['newspaper'] = self.name
        item['imgs'] = imgs
        yield item


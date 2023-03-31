# -*- coding: utf-8 -*-
import json
import requests
import scrapy
import re
from newscrapy.items import NewscrapyItem
from scrapy import FormRequest
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
from urllib import parse


class mySpider(CrawlSpider):

    name = "aqwb"
    newspapers = '安庆晚报'

    def pre_fetch_url(self):
        url_month = 'http://aqdzb.aqnews.com.cn/epaper/read.do?m=getIssueByMonth'
        payload = {
            'newspaperId': '2',
            'date': '2023-02-21',
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Host': 'aqdzb.aqnews.com.cn',
            'Referer': 'http://aqdzb.aqnews.com.cn/epaper/read.do?m=i&iid=11042&idate=2_2023-03-01',
            # 'Cookie': 'JSESSIONID=6A67FCA5AD2C1CE5ADEEA6A066B815CA; __jsluid_h=dffec1e3d9a5600ded393128991632f7',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 Edg/106.0.1370.47'
        }
        r = requests.post(url_month, data=payload, headers=headers)
        return r.json()['data']

    def start_requests(self):
        paths = self.pre_fetch_url()
        print(paths)
        urls = [urljoin('http://aqdzb.aqnews.com.cn', item['path']) for item in paths]
        for url in urls:
            yield FormRequest(url, dont_filter=True)

    rules = (
        Rule(LinkExtractor(allow=('/epaper/read.do.+?eid=\d+&idate=.+?'))),
        Rule(LinkExtractor(allow=('/epaper/read.do.+?sid=\d+&idate=.+?')), callback="parse_item")
    )

    def parse_item(self, response):
        # print(response.text)
        title = response.xpath("//p[@class='articleTitle']/text()").get()
        title2 = response.xpath("//p[@class='articleTitle2']/text()").get()
        if title2:
            title = '/'.join([title, title2])
        content = response.xpath("//div[@class='articleContent']").xpath("string(.)").get()
        url = response.url
        date = re.findall("idate=\d+_(\d{4}-\d{2}-\d{2})", url)
        if date:
            date = date[0]
        else:
            date = ''
        imgs = response.xpath("//div[@id='article_image']/img//@src").getall()
        imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
        html = response.text

        item = NewscrapyItem()
        item['title'] = title
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = response.url
        item['newspaper'] = self.newspapers
        print(item)
        # item['html'] = html
        yield item

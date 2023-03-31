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

    name = "yzwb"
    newspapers = '颍州晚报'

    def pre_fetch_url(self):
        url_month = 'http://test.fynews.net/epaper/read.do?m=getIssueByMonth'
        payload = {
            'newspaperId': '2',
            'date': '2022-08-19',
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Host': 'test.fynews.net',
            'Referer': 'http://test.fynews.net/epaper/read.do?m=i&iid=2474&eid=24387&idate=2_2022-08-19',
            # 'Cookie': 'JSESSIONID=6A67FCA5AD2C1CE5ADEEA6A066B815CA; __jsluid_h=dffec1e3d9a5600ded393128991632f7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44'
        }
        r = requests.post(url_month, data=payload, headers=headers)
        return r.json()['data']

    def start_requests(self):
        paths = self.pre_fetch_url()
        print(paths)
        urls = [urljoin('http://test.fynews.net', item['path']) for item in paths]
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
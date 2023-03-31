from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "rmydb"
    newspapers = "人民邮电报"
    allowed_domains = ['paper.cnii.com.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y_%m_%d")
        template = "https://paper.cnii.com.cn/item/rmydb_{date}_1.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('item/rmydb_\d+_\d+_\d+_\d+.html'))),
        Rule(LinkExtractor(allow=('article/rmydb_\d+_\d+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            body = response.xpath("//div[@class='title-container']")
            title = body.xpath(".//h2").xpath("string(.)").get()
            content = response.xpath(".//div[@align='left']//font").xpath("string(.)").getall()
            url = response.url
            date = body.xpath(".//p[@class='date']").xpath("string(.)").getall()
            imgs = response.xpath(".//div[@align='center']//img/@src").getall()
            imgs = [parse.urljoin(url, imgurl) for imgurl in imgs]
            html = response.text
        except Exception as e:
            return
        
        item = NewscrapyItem()
        item['title'] = title
        item['content'] = content
        item['date'] = date
        item['imgs'] = imgs
        item['url'] = response.url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item
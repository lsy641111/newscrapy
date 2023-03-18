from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "hxdsb"
    newspapers = "海峡都市报"
    allowed_domains = ['szb.mnw.cn']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y/%m%d")
        template = "http://szb.mnw.cn/{date}/list_1.shtml"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('\d+/\d+/list_\d+.shtml'))),
        Rule(LinkExtractor(allow=('\d+/\d+/\d+.shtml')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath(".//div[@id='content']/table[1]/tbody/tr/td/span[2]").xpath("string(.)").get()
            content = response.xpath(".//div[@id='content']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("/(\d+/\d+)/\d+", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[6:8]])
            html = response.text
        except Exception as e:
            return
        
        item = NewscrapyItem()
        item['title'] = title
        item['content'] = content
        item['date'] = date
        item['url'] = response.url
        item['newspaper'] = self.newspapers
        item['html'] = html
        yield item
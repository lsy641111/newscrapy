from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "zjsb"
    newspapers = "珠江时报"
    allowed_domains = ['szb.nanhaitoday.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "https://szb.nanhaitoday.com/epaper/zjsb/html/{date}/node_4921.htm"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/node_\d+.htm'))),
        Rule(LinkExtractor(allow=('html/\d+-\d+/\d+/content_\d+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath(".//div[@id='print_area']/h1").xpath("string(.)").getall()
            content = response.xpath(".//div[@id='content']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("html/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath(".//div[@id='content']//img/@src").getall()
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
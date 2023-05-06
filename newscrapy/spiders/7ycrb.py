from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "ycrb"
    newspapers = "宜春日报"
    allowed_domains = ['epaper.newsyc.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y%m/%d")
        template = "https://epaper.newsyc.com:9443/ycrb/pc/{date}/node_01.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('pc/\d+\d+/\d+/node_\d+.html'))),
        Rule(LinkExtractor(allow=('pc/content/\d+\d+/\d+/content_\d+.html')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath(".//h2[@id='Title']").xpath("string(.)").get()
            content = response.xpath(".//div[@class='article-content']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("content/(\d+\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[4:6], date[7:9]])
            imgs = response.xpath(".//div[@class='attachment']//img/@src").getall()
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
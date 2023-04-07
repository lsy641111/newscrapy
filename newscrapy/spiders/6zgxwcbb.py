from scrapy import FormRequest
import re
from newscrapy.items import NewscrapyItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from newscrapy.tools import dateGen
from urllib import parse


class mySpider(CrawlSpider):
    name = "zgxwcbb"
    newspapers = "中国新闻出版报"
    allowed_domains = ['epaper.chinaxwcb.com']
    
    def start_requests(self):
        dates = dateGen(self.start, self.end, "%Y-%m/%d")
        template = "https://epaper.chinaxwcb.com/epaper/{date}/node_1.html"
        for d in dates:
            yield FormRequest(template.format(date = d))

    rules = (
        Rule(LinkExtractor(allow=('epaper/\d+-\d+/\d+/node_\d+.htm'))),
        Rule(LinkExtractor(allow=('epaper/\d+-\d+/\d+/content_\d+.htm')), callback="parse_item")
    )

    def parse_item(self, response):
        try:
            title = response.xpath(".//div[@id='news_content']/h1").xpath("string(.)").getall()
            content = response.xpath(".//div[@id='news_content']//p").xpath("string(.)").getall()
            url = response.url
            date = re.search("epaper/(\d+-\d+/\d+)/content", url).group(1)
            date = '-'.join([date[0:4], date[5:7], date[8:10]])
            imgs = response.xpath(".//div[@id='news_content']//img/@src").getall()
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
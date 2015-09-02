import scrapy
from datetime import datetime

class Post(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    raw = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    published = scrapy.Field()
    comments = scrapy.Field()
    ip = scrapy.Field()

class PTTSpider(scrapy.Spider):
    name = 'pttspider'
    start_urls = ['http://www.ptt.cc/bbs/studyabroad/']

    def parse(self, response):
        max_index_str = response.css("#action-bar-container .btn-group.pull-right a:nth-child(2)::attr(\"href\")").re("index(\d*)\.html")[0]
        max_index = int(max_index_str)

        for index in range(max_index-1, max_index + 1):
            yield scrapy.Request("https://www.ptt.cc/bbs/studyabroad/index%s.html" % index, self.parse_index_page)

    def parse_index_page(self, response):
        for a in response.css('.title a'):
            item = Post()
            link, title=  a.re("href=\"(.*)\">(.*)<\/a>")
            item["url"] = link
            item["title"] = title
            request = scrapy.Request(response.urljoin(link), self.parse_article)
            request.meta['item'] = item
            yield request

    def parse_article(self, response):
        item = response.meta['item']
        item["raw"] = response.css("#main-content")[0].extract()
        item["content"] = response.css("#main-content::text")[0].extract()
        item["author"] = response.css(".article-meta-value::text")[0].extract()
        d = response.css(".article-meta-value::text")[3].extract()
        item["published"] = datetime.strptime(d, "%a %b\t%d %H:%M:%S %Y")
        item["ip"] = response.css(".f2").re("(?:[0-9]{1,3}\.){3}[0-9]{1,3}")[0]
        comments = []
        for push in response.css(".push"):
            p = {}
            p["pushTag"] =  push.css(".push-tag::text")[0].extract().strip()
            p["user"] = push.css(".push-userid::text")[0].extract().strip()
            p["content"]=push.css(".push-content::text")[0].extract().strip()[2:]
            p["ipdatetime"] = push.css(".push-ipdatetime::text")[0].extract().strip()
            comments.append(p)
        yield item

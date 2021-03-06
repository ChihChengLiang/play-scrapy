# -*- coding: utf-8 -*-
import scrapy
from studyabroad.items import Post
from datetime import datetime
import re

class PTTSpider(scrapy.Spider):
    name = 'pttspider'
    start_urls = ['http://www.ptt.cc/bbs/studyabroad/']

    def parse(self, response):
        max_index_str = response.css("#action-bar-container .btn-group.pull-right a:nth-child(2)::attr(\"href\")").re("index(\d*)\.html")[0]
        max_index = int(max_index_str)

        for index in range(1, max_index + 1):
            yield scrapy.Request("http://www.ptt.cc/bbs/studyabroad/index%s.html" % index, self.parse_index_page)

    def parse_index_page(self, response):
        for entry in response.css('.r-ent'):
            if len(entry.css(".title a"))>0:
                item = Post()
                link, title=  entry.css(".title a")[0].re("href=\"(.*)\">(.*)<\/a>")
                item["url"] = link
                p0 = re.compile(ur'/(M\.[\d]*.*)\.html')
                item["uid"] = re.search(p0, link).group(1)
                item["title"] = title
                p = re.compile(ur'\[(.*)\]')
                tag = re.search(p, title)
                if tag:
                    item["tag"] =tag.group(1)
                push_span = entry.css(".nrec span::text")
                if len(push_span)>0:
                    item["total_push"] = push_span[0].extract()
                request = scrapy.Request(response.urljoin(link), self.parse_article)
                request.meta['item'] = item
                yield request

    def parse_article(self, response):
        item = response.meta['item']
        item["raw"] = response.css("#main-content")[0].extract()
        if len(response.css("#main-content::text"))>0:
            item["content"] = response.css("#main-content::text")[0].extract()
        meta_value = response.css(".article-meta-value::text")
        if len(meta_value)>0:
            item["author"] = meta_value[0].extract()
        elif len(meta_value)>=4:
            d = response.css(".article-meta-value::text")[3].extract()
            item["published"] = datetime.strptime(d, "%a %b\t%d %H:%M:%S %Y")
        iptag = response.css(".f2").re("(?:[0-9]{1,3}\.){3}[0-9]{1,3}")
        if len(iptag)>0:
            item["ip"] = iptag[0]
        comments = []
        for push in response.css(".push"):
            p = {}
            p["pushTag"] =  push.css(".push-tag::text")[0].extract().strip()
            p["user"] = push.css(".push-userid::text")[0].extract().strip()
            p["content"]=push.css(".push-content::text")[0].extract().strip()[2:]
            p["ipdatetime"] = push.css(".push-ipdatetime::text")[0].extract().strip()
            comments.append(p)
        item["comments"] = comments
        yield item

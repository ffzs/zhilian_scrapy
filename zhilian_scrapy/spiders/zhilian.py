# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from zhilian_scrapy.items import ZhilianScrapyItem

class ZhilianSpider(scrapy.Spider):
    name = "zhilian"
    # 限定爬取网址范围是在这个网址内，超出范围的网址将会被过滤掉
    allowed_domains = ["m.zhaopin.com"]
    #网站爬取的起始位置
    start_urls = ['https://m.zhaopin.com/beijing-530/?keyword=python&pageindex=1&maprange=3&islocation=0']

    def parse(self, response):
        # 注意这里是response.body,不是.text
        soup = BeautifulSoup(response.body, "lxml")
        all_sec = soup.find("div", class_="r_searchlist positiolist").find_all("section")
        for sec in all_sec:
            data_link = sec.find("a", class_="boxsizing")["data-link"]
            url = 'https://m.zhaopin.com'+data_link
            yield scrapy.Request(url, callback=self.parse_item,dont_filter=True)

        if soup.find("a", class_="nextpage"):
            next_url = "https://m.zhaopin.com"+soup.find("a",class_="nextpage")["href"]
            print(next_url)
            yield scrapy.Request(next_url, callback=self.parse,dont_filter=True)

    def parse_item(self, response):
        item = ZhilianScrapyItem()
        item["job_link"] = response.url
        item["job_name"] = response.xpath('//*[@class="job-name fl"]/text()')[0].extract()
        item["company"] = response.xpath('//*[@class="comp-name"]/text()')[0].extract()
        if response.xpath('//*[@class="add"]/text()'):
            item["address"] = response.xpath('//*[@class="add"]/text()')[0].extract()
        else:
            item["address"] = ""
        item["job_info"] = "".join(response.xpath("//*[@class='about-main']/p/text()").extract())
        item["salary"] = response.xpath('//*[@class="job-sal fr"]/text()')[0].extract()
        item["job_tags"] = ";".join(response.xpath('//*[@class="tag"]/text()').extract())
        yield item





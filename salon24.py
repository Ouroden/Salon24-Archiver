# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
import json


import time
class P:
    p=[]


def between(value, a, b):
            # Find and validate before-part.
            pos_a = value.find(a)
            if pos_a == -1: return ""
            # Find and validate after part.
            pos_b = value.rfind(b)
            if pos_b == -1: return ""
            # Return middle part.
            adjusted_pos_a = pos_a + len(a)
            if adjusted_pos_a >= pos_b: return ""
            return value[adjusted_pos_a:pos_b-3] # -3 hack

class Salon24Spider(scrapy.Spider):
    name = 'salon24'
    allowed_domains = ['salon24.pl']
    start_urls = ['https://www.salon24.pl/katalog-blogow/,alfabetycznie,1']




    def parse(self, response):



        self.log('I just visited: ' + response.url)
        blog_list= response.css('ul.blog-list')

        next_page = response.css('ul.pager').css("li").extract()[-1]
        #self.log('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ' + str(next_page.find("Następna strona")) )

        for li in blog_list.css('li'):
            result = {
                'nick': li.css('span.blog-list__nick::text').extract_first(),
                'blog_name': li.css('span.blog-list__blog-name::text').extract_first(),
                'link': (between(li.get(), "//", "img src")) #not the best way

            }
            P.p.append(result)

        x = 1
        while response.url[-x] != ",":
            x = x + 1

        next = int(response.url[-x + 1:]) + 1

        if (next<30 ) & (next_page.find("Następna strona")>0) : # delete (next<30 ) & to parse all blogs

            url="https://www.salon24.pl/katalog-blogow/,alfabetycznie,"+ str(next)

            return scrapy.Request(url,
                             callback=self.parse)



        
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})


Salon = Salon24Spider()
process.crawl(Salon)
process.start()

with open('data.json', 'a') as json_file:
    json.dump(P.p, json_file)



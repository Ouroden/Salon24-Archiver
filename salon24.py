# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
import json


import time
class Result:

    def __init__(self):
        self.data=[]
        self.counter=0


class Salon24Spider(scrapy.Spider):
    name = 'salon24'
    allowed_domains = ['salon24.pl']
    start_urls = ['https://www.salon24.pl/']



    def parse(self, response):

        url = "https://www.salon24.pl/katalog-blogow/,alfabetycznie," + str(self.input)
        return scrapy.Request(url,
                              callback=self.parseBlogs)

    def parseBlogs(self, response):



        self.log('I just visited: ' + response.url)# +str(self.input))
        blog_list= response.css('ul.blog-list')

        next_page = response.css('ul.pager').css("li").extract()[-1]
        #self.log('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ' + str(next_page.find("Następna strona")) )

        for li in blog_list.css('li'):
            result = {
                'nick': li.css('span.blog-list__nick::text').extract_first(),
                'blog_name': li.css('span.blog-list__blog-name::text').extract_first(),
                'blog_link': (self.between(li.get(), "//", "img src",3)), #not the best way multiple " in expression need hack
                'articles':[],
                'tmp_articles':[]
            }
            self.result.data.append(result)

        x = 1
        while response.url[-x] != ",":
            x = x + 1

        next = int(response.url[-x + 1:]) + 1

        if (next<self.input+2 ) & (next_page.find("Następna strona")>0) : # delete (next<30 ) & to parse all blogs

            url="https://www.salon24.pl/katalog-blogow/,alfabetycznie,"+ str(next)

            return scrapy.Request(url,
                             callback=self.parseBlogs)
        else:


            url="https://"+self.result.data[0]['blog_link']

            return scrapy.Request(url,
                                  callback=self.parseSingleBlog)

    def parseSingleBlog(self, response):
            self.log('I just visited: ' + response.url)


            for article in response.css('article.posts').css('h2').extract():
                link,title = self.between( article, "//", "</a>").split("\">")
                result = {
                    "title": title,
                    "article_link": link
                }
                self.result.data[self.result.counter]['tmp_articles'].append(result)

            self.result.counter += 1
            if(self.result.counter<3):
                url = "https://" + self.result.data[self.result.counter]['blog_link']

                return scrapy.Request(url,
                                  callback=self.parseSingleBlog)




            else:
                    self.result.counter = 0
                    return scrapy.Request('https://www.salon24.pl',
                                      callback=self.findArticle)

    def findArticle(self, response):
        self.log('I just visited: ' + response.url)

        while (self.result.data[self.result.counter]['tmp_articles']):

            article = self.result.data[self.result.counter]['tmp_articles'].pop(0)
            self.log(article['article_link'])
            self.result.data[self.result.counter]['articles'].append(article)

            url ="https://"+article['article_link']
            return scrapy.Request(url,  dont_filter=True,
                                  callback=self.parseArticle)


        self.result.counter += 1
        if self.result.counter<3:

            url = "https://" + self.result.data[self.result.counter]['blog_link']
            return scrapy.Request(url, dont_filter=True,
                                  callback=self.findArticle)

        # # url = "https://" + self.result.data[self.result.counter]['tmp_articles']
        #

    def parseArticle(self, response):
        self.log("P A R S O W A N K O"  )
        self.result.data[self.result.counter]['articles'][-1]['content']=response.css('div.article-content').extract()

        url = "https://salon24.pl"
        return scrapy.Request(url, dont_filter=True,
                              callback=self.findArticle)


    def between(self, value, a, b,hack=0):
            # Find and validate before-part.
            pos_a = value.find(a)
            if pos_a == -1: return ""
            # Find and validate after part.
            pos_b = value.rfind(b)
            if pos_b == -1: return ""
            # Return middle part.
            adjusted_pos_a = pos_a + len(a)
            if adjusted_pos_a >= pos_b: return ""
            return value[adjusted_pos_a:pos_b - hack]  # -3 hack






process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

blog_list=1234

p=Result()
p2=Result()
p3=Result()
start=time.time()

process.crawl( Salon24Spider(),input=1, result=p)
# process.crawl( Salon24Spider(),input=30, result=p2)
# process.crawl( Salon24Spider(),input=60,result=p3)
# process.crawl( Salon24Spider(),input=90)
# process.crawl( Salon24Spider(),input=120)
# process.crawl( Salon24Spider(),input=150)
# process.crawl( Salon24Spider(),input=180)


process.start()

print(p.data[0]["articles"],p.data[1]["articles"],p.data[2]["articles"])
# print(p2.data[0]["articles"],p2.data[1]["articles"],p2.data[2]["articles"])
# print(p3.data[0]["articles"],p2.data[1]["articles"],p3.data[2]["articles"])
print(p.data)
print(time.time()-start)

with open('data.json', 'a') as json_file:
    json.dump(p.data, json_file,ensure_ascii=False)



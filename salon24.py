# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
import json
import urllib.request
import datetime
import time
class Result:

    def __init__(self):
        self.data=[]
        self.counter=0


class Salon24Spider(scrapy.Spider):
    name = 'salon24'
    allowed_domains = ['salon24.pl']
    start_urls = ['https://www.salon24.pl/']
    """
    def __init__(self, input, amount,result):
        self.input=input
        self.amount=amount
        self.result=result
    """
    def parse(self, response):
        self.log(self.result.counter)

        self.log(self.amount)
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

        if (next<self.input +self.amount ) and (next_page.find("Następna strona")>0) : # delete (next<30 ) & to parse all blogs

            url="https://www.salon24.pl/katalog-blogow/,alfabetycznie,"+ str(next)

            return scrapy.Request(url,
                             callback=self.parseBlogs)
        else:


            url="https://"+self.result.data[0]['blog_link']

            return scrapy.Request(url,
                                  callback=self.parseSingleBlog)

    def parseSingleBlog(self, response):
            self.log('I just visited: ' + response.url)

            if(response.url=="https://www.salon24.pl"):
                self.result.data[self.result.counter]['followers'] = ""
                self.result.data[self.result.counter]['views'] = ""
                self.result.data[self.result.counter]['articles_amount'] = ""
                self.result.data[self.result.counter]['blog_description'] = ""
                self.log("Portal Error, link to blog doesnt exist")
            self.log(self.result.counter)
            if not 'followers' in self.result.data[self.result.counter]:

                details = response.css('div.user-header__counters').extract_first()
                if details:
                    obserwujących = (self.between(details, "</i>", "obserwujących"))
                    obserwujących = self.before(obserwujących, "<span>")
                    # print(obserwujących)

                    details = self.after(details, "obserwujących")
                    notek = self.between(details, "</i>", "not")
                    notek = self.before(notek, "<span>")
                    # print(notek)

                    details = self.after(details, "not")
                    odslon = (self.between(details, "</i>", "odsło"))
                    odslon = self.before(odslon, "<span>")
                    # print(odslon)

                    descritpion=response.css('div.user-about__content').css('div.too-high::text').extract_first()
                    if descritpion:
                        descritpion=descritpion.replace("\n" ,"").replace("\t","")

                    details={
                        'followers': obserwujących,
                        'views': odslon,
                        'articles_amount': notek,
                        'blog_description': descritpion
                    }
                    self.result.data[self.result.counter]['followers']=obserwujących
                    self.result.data[self.result.counter]['views'] = odslon
                    self.result.data[self.result.counter]['articles_amount'] = notek
                    self.result.data[self.result.counter]['blog_description'] = descritpion

            for article in response.css('article.posts').css('h2').extract():
                link,title = self.between( article, "//", "</a>").split("\">")
                result = {
                    "title": title,
                    "article_link": link
                }
                self.result.data[self.result.counter]['tmp_articles'].append(result)

            if(response.css('ul.pager').css("li").extract()):
                next=response.css('ul.pager').css("li").extract()[-1]
                next_exist=next.find("Następna strona")
                if(next_exist>0):
                    url= "https://"+self.between(next,"//","\" alt")
                    return scrapy.Request(url, dont_filter=True,
                                          callback=self.parseSingleBlog)

            self.result.counter += 1


            if self.result.counter + 0< self.amount *18 and len(self.result.data)>self.result.counter:
                url = "https://" + self.result.data[self.result.counter]['blog_link']

                return scrapy.Request(url,dont_filter=True,
                                  callback=self.parseSingleBlog)



            else:
                    self.result.counter = 0
                    return scrapy.Request('https://www.salon24.pl',dont_filter=True,
                                      callback=self.findArticle)

    def findArticle(self, response):
            self.log('I just visited: ' + response.url)
            self.log(self.result.counter)
            self.log(len(self.result.data))

            while (self.result.data[self.result.counter]['tmp_articles']):

                article = self.result.data[self.result.counter]['tmp_articles'].pop(0)
                self.log(article['article_link'])
                self.result.data[self.result.counter]['articles'].append(article)

                url ="https://"+article['article_link']
                return scrapy.Request(url,  dont_filter=True,
                                      callback=self.parseArticle)


            self.result.counter += 1
            if self.result.counter<(self.amount*18)  and  len(self.result.data)>self.result.counter:

                url = "https://" + self.result.data[self.result.counter]['blog_link']
                return scrapy.Request(url, dont_filter=True,
                                      callback=self.findArticle)

        # # url = "https://" + self.result.data[self.result.counter]['tmp_articles']
        #

    def parseArticle(self, response):
        self.log("P A R S O W A N K O"  )
        self.result.data[self.result.counter]['articles'][-1]['content']=response.css('div.article-content').extract_first().replace("\n","").replace("\t","")

        header=response.css('article.article').css('header')
        categ=""
        for cat in header.css('ul').css('li').extract():
            categ+=self.between(cat,"\">","</a>") + " " # maybe should be table?
        self.result.data[self.result.counter]['articles'][-1]['categories'] = categ
        time=header.css('time::text').extract_first().replace("\n" ,"").replace("\t","")
        self.result.data[self.result.counter]['articles'][-1]['date'] = time
        views=header.css('span::text').extract_first().replace("\n" ,"").replace("\t","")
        self.result.data[self.result.counter]['articles'][-1]['views'] = views
        self.result.data[self.result.counter]['articles'][-1]['article_id']=""
        self.result.data[self.result.counter]['articles'][-1]['comments']=[]


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

    def before(self,value, a):
            # Find first part and return slice before it.
            pos_a = value.find(a)
            if pos_a == -1: return ""
            return value[0:pos_a]

    def after(self,value, a):
            # Find and validate first part.
            pos_a = value.rfind(a)
            if pos_a == -1: return ""
            # Returns chars after the found string.
            adjusted_pos_a = pos_a + len(a)
            if adjusted_pos_a >= len(value): return ""
            return value[adjusted_pos_a:]



process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

blog_list=12345

p=Result()
p2=Result()
p3=Result()
p4=Result()
p5=Result()
p6=Result()
p7=Result()
start=time.time()

process.crawl( Salon24Spider(),input=1, amount=5, result=p)
process.crawl( Salon24Spider(),input=6, amount=5,result=p2)
process.crawl( Salon24Spider(),input=11,amount=5 ,result=p3)
process.crawl( Salon24Spider(),input=16, amount=5,result=p4)
process.crawl( Salon24Spider(),input=21,amount=5,result=p5)
process.crawl( Salon24Spider(),input=26,amount=5,result=p6)
process.crawl( Salon24Spider(),input=31,amount=5,result=p7)



process.start()

#print(p.data[2])
# print(p2.data[0]["articles"],p2.data[1]["articles"],p2.data[2]["articles"])
# print(p3.data[0]["articles"],p2.data[1]["articles"],p3.data[2]["articles"])
# for tmp in p.data:
#     print(tmp['blog_description'])


print(len(p.data))
print(len(p2.data))
print(len(p3.data))
print(len(p4.data))
print(len(p5.data))
print(len(p6.data))
print(len(p7.data))


print(time.time()-start)

for blog in p.data:
    for article in blog["articles"]:
        alink=article["article_link"]
        blink=blog["blog_link"]

        #print(alink,blink)


        article_id=(alink[len(blink):]).split(",", 1)[0]
        article["article_id"]=article_id
        json_url = urllib.request.urlopen(
            'https://www.salon24.pl/comments-api/comments?sourceId=Post-'+article_id+'&sort=NEWEST')
        data = json.loads(json_url.read())
        type(data)

        print(article_id)
        for comment in data['data']["comments"]['data']:

            #print(data['data']["users"][comment['userId']]["nick"] + " : ", comment['content'])

            result ={
                "author": data['data']["users"][comment['userId']]["nick"],
                "content": comment['content'],
                "votes": comment['votes'],
                "likes": comment['likes'],
                "dislikes": comment['dislikes'],
                "date":  datetime.datetime.fromtimestamp(
                                    int(comment['created'][:-3])
                                    ).strftime('%Y-%m-%d %H:%M:%S'),
                "comment_id": comment['id'],
                "replies_amount": comment['replies'],
                "deleted":comment['deleted'],
                "answers": []


            }
            article["comments"].append(result)

            if (comment['replies']):

                for answer in comment["comments"]["data"]:
                    result = {
                        "author": data['data']["users"][answer['userId']]["nick"],
                        "content": answer['content'],
                        "votes": answer['votes'],
                        "likes": answer['likes'],
                        "dislikes": answer['dislikes'],
                        "date": datetime.datetime.fromtimestamp(
                            int(answer['created'][:-3])
                        ).strftime('%Y-%m-%d %H:%M:%S'),
                        "comment_id": answer['id'],
                        "deleted": answer['deleted'],


                    }


                    #print(data['data']["users"][answer['userId']]["nick"] + " : ", answer['content'])

                    article["comments"][-1]["answers"].append(result)


print(time.time()-start)

with open('data.json', 'w') as json_file:
    json.dump(p.data, json_file,ensure_ascii=False)



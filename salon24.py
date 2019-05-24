# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
import json
import urllib.request
import datetime
import time
import threading
from pymongo import MongoClient
from DbManager import DbManager


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
                    obserwujących = (self.between(details, "</i>", "obserwuj"))
                    obserwujących = self.before(obserwujących, "<span>")
                    # print(obserwujących)

                    details = self.after(details, "obserwuj")
                    notek = self.between(details, "</i>", "not")
                    notek = self.before(notek, "<span>")
                    # print(notek)

                    details = self.after(details, "not")
                    odslon = (self.between(details, "</i>", "odsło"))
                    odslon = self.before(odslon, "<span>")
                    if 'k' in odslon:
                        odslon = odslon.replace("k", "000")

                    # print(odslon)

                    descritpion=response.css('div.user-about__content').css('div.too-high::text').extract_first()
                    if descritpion:
                        descritpion=descritpion.replace("\n" ,"").replace("\t","")


                    self.result.data[self.result.counter]['followers']=int(obserwujących)
                    self.result.data[self.result.counter]['views'] = int(odslon)
                    self.result.data[self.result.counter]['articles_amount'] = int(notek)
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
        self.result.data[self.result.counter]['articles'][-1]['views'] = int(views.split(" ")[0])#modyfied
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


def parseComments(data):
    for blog in data:
        for article in blog["articles"]:
            alink = article["article_link"]
            blink = blog["blog_link"]

            # print(alink,blink)

            article_id = (alink[len(blink):]).split(",", 1)[0]
            article["article_id"] = article_id

            for i in range(5):
                try:
                    json_url = urllib.request.urlopen(
                        'https://www.salon24.pl/comments-api/comments?sourceId=Post-' + article_id + '&sort=NEWEST&limit=100000')
                    data = json.loads(json_url.read())
                    type(data)
                    break
                except ValueError:
                    time.sleep(1)




            # print(article_id)
            for comment in data['data']["comments"]['data']:

                # print(data['data']["users"][comment['userId']]["nick"] + " : ", comment['content'])

                result = {
                    "author": data['data']["users"][comment['userId']]["nick"],
                    "content": comment['content'],
                    "votes": comment['votes'],
                    "likes": comment['likes'],
                    "dislikes": comment['dislikes'],
                    "date": datetime.datetime.fromtimestamp(
                        int(comment['created'][:-3])
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    "comment_id": comment['id'],
                    "replies_amount": comment['replies'],
                    "deleted": comment['deleted'],
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

                        # print(data['data']["users"][answer['userId']]["nick"] + " : ", answer['content'])

                        article["comments"][-1]["answers"].append(result)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

def tmp():

    p = [Result(), Result()]
    process.crawl(Salon24Spider(), input=1, amount=1, result=p[0])
    process.crawl(Salon24Spider(), input=1240, amount=1, result=p[1])
    process.start()

    t1 = threading.Thread(target=parseComments, args=(p[0].data,))
    t2 = threading.Thread(target=parseComments, args=(p[1].data,))
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    with open('data.json', 'w') as json_file:
        json.dump(p[0].data, json_file, ensure_ascii=False)
        json.dump(p[1].data, json_file, ensure_ascii=False)
def main():
    print("Connecting to Database...")

    client = MongoClient('localhost:27017')
    db = client.Blogs
    dbManager = DbManager(db)

    print("Connected successfully.")

    print("Downloading all blogs without comments...")
    start = time.time()

    # p = [Result(), Result()]
    # process.crawl(Salon24Spider(), input=1, amount=1, result=p[0])
    # process.crawl(Salon24Spider(), input=2, amount=1, result=p[1])
    # process.start()

    results = []
    for i in range(0, 95):
        results.append(Result())

    for i in range(0, 95):
        process.crawl(Salon24Spider(), input=1+(i*13), amount=13, result=results[i])

    process.start()

    print("Took: ", time.time() - start, "sec")

    print("Downloading all comments...")
    start = time.time()

    # t1 = threading.Thread(target=parseComments, args=(p[0].data, ))
    # t2 = threading.Thread(target=parseComments, args=(p[1].data, ))
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()

    threads = []
    for i in range(0, 95):
        t = threading.Thread(target=parseComments, args=(results[i].data, ))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Took: ", time.time() - start, "sec")

    print("Inserting to Database...")
    start = time.time()



    #     # for i in range (0,95):
    #     #      json.dump(p[i].data, json_file, ensure_ascii=False)



    for result in results:
        for blog in result.data:
            dbManager.insert_entry(blog)

    print("Took: ", time.time() - start, "sec")



if __name__ == '__main__':
    # number of pages with blogs = 1235
    #main()
    tmp()

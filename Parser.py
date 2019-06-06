import scrapy
from scrapy.crawler import CrawlerProcess
import datetime

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
        """      
        self.log('I just visited: ' + url)# +str(self.input))
        a={"ulr" : url
           }
        with open('data.json', 'a') as json_file:
            json.dump(a, json_file, ensure_ascii=False)
        """
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
                    #if not "10,wszystkie" in url: #edited
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
        raw_date=self.toRawDate(time)
        self.result.data[self.result.counter]['articles'][-1]['date'] = time
        self.result.data[self.result.counter]['articles'][-1]['raw_date'] = raw_date
        views=header.css('span::text').extract_first().replace("\n" ,"").replace("\t","")
        self.result.data[self.result.counter]['articles'][-1]['views'] = int(views.split(" ")[0])#modyfied
        self.result.data[self.result.counter]['articles'][-1]['article_id']=""
        self.result.data[self.result.counter]['articles'][-1]['comments']=[]


        url = "https://salon24.pl"
        return scrapy.Request(url, dont_filter=True,
                              callback=self.findArticle)

    def toRawDate(self, time):
        def monthToInt(month):
            if month.startswith('sty'):
                return (1)
            elif month.startswith('lut'):
                return (2)
            elif month.startswith('marz'):
                return (3)
            elif month.startswith('kwie'):
                return (4)
            elif month.startswith('maj'):
                return (5)
            elif month.startswith('czerw'):
                return (6)
            elif month.startswith('lip'):
                return (7)
            elif month.startswith('sier'):
                return (8)
            elif month.startswith('wrze'):
                return (9)
            elif month.startswith('paź'):
                return (10)
            elif month.startswith('lis'):
                return (11)
            elif month.startswith('gru'):
                return (12)
            else:
                return 1


        split = time.split(" ")
        day = int(split[0])
        month = int(monthToInt(split[1]))
        year = int(split[2][:-1])
        clock = split[3].split(":")
        hour = int(clock[0])
        minute = int(clock[1])

        date = datetime.datetime(year, month, day, hour, minute)

        raw_date = int(date.timestamp())
        return(raw_date)


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
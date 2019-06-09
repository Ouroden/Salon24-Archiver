#!/bin/python
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
import Parser
import DownloadManager as DM


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

class Result:

    def __init__(self):
        self.data=[]
        self.counter=0


def smallDataSizeTest():
    p = [Result(), Result()]
    process.crawl(Parser.Salon24Spider(), input=1, amount=1, result=p[0])
    process.crawl(Parser.Salon24Spider(), input=2, amount=1, result=p[1])
    process.start()

    t1 = threading.Thread(target=DM.parseComments, args=(p[0].data,))
    t2 = threading.Thread(target=DM.parseComments, args=(p[1].data,))
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    with open('data.json', 'w') as json_file:
        json.dump(p[0].data, json_file, ensure_ascii=False)
        json.dump(p[1].data, json_file, ensure_ascii=False)


def main():

    print("Downloading all blogs without comments...")
    start = time.time()

    results = []

    for i in range(0, 100):
        results.append(Result())
    j=0
    for i in range(1 , 1300, 13):
        process.crawl(Parser.Salon24Spider(), input=1+(i), amount=13, result=results[j]) #edited
        j+=1
    process.start()

    print("Took: ", time.time() - start, "sec")

    print("Downloading all comments...")
    start = time.time()


    data=[[],[],[],[],[]];
    for i in range (0,100,5):
        data[0].extend(results[i].data)
        data[1].extend(results[i+1].data)
        data[2].extend(results[i+2].data)
        data[3].extend(results[i+3].data)
        data[4].extend(results[i+4].data)

    threads = []
    for i in range(0, 5):
        t = threading.Thread(target=DM.parseComments, args=(data[i], ))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Took: ", time.time() - start, "sec")

    print("Inserting to Database...")
    start = time.time()



    print("Connecting to Database...")

    client = MongoClient('localhost:27017')
    db = client.SalonBaza
    dbManager = DbManager(db)

    print("Connected successfully.")

    for result in data:
        for blog in result:
            dbManager.insert_entry(blog)

    print("Took: ", time.time() - start, "sec")


if __name__ == '__main__':
    # number of pages with blogs = 1235
    main()
    #smallDataSizeTest()

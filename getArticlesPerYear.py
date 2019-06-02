#!/bin/python

from pymongo import MongoClient
from pprint import pprint
import datetime

def main(blogs):

    tab = {}
    tab[2006] = 1136070000
    tab[2007] = 1167606000
    tab[2008] = 1199142000
    tab[2009] = 1230764400
    tab[2010] = 1262300400
    tab[2011] = 1293836400
    tab[2012] = 1325372400
    tab[2013] = 1356994800
    tab[2014] = 1388530800
    tab[2015] = 1420066800
    tab[2016] = 1451602800
    tab[2017] = 1483225200
    tab[2018] = 1514761200
    tab[2019] = 1546297200
    tab[2020] = 9999999999
    result = []
    for y in range(2007, 2020):

        pipeline = [
            {"$unwind": "$articles"},
            {"$match": {
                    "articles.raw_date": {"$lt": tab[y]}
                }
            },
            {"$group": {
                "_id": {"title": "$articles.title", "date": "$articles.raw_date"},
                "total": {"$sum": 1},
            }},
            {"$sort": {"total": -1}}
        ]

        cursor = blogs.aggregate(pipeline)
        resultTmp = list(cursor)

        print(y, ": ", len(resultTmp))
        result.append(len(resultTmp))

    print(result)


if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Salon
    blogs = db["Blogs"]

    try:
        main(blogs)
    except Exception as e:
        print(str(e))



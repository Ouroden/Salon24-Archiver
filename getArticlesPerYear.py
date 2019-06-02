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
    for y in range(2007, 2021):

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

    return(result)


if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Salon
    blogs = db["Blogs"]



    try:
        results=main(blogs)
        print(results)

        import matplotlib.pyplot as plt;

        plt.rcdefaults()
        import numpy as np
        import matplotlib.pyplot as plt

        objects = ('2006', '2007', '2008', '2009','2010', '2011', '2012', '2013','2014', '2015', '2016', '2017','2018', '2019')
        y_pos = np.arange(len(objects))
        performance = results

        plt.bar(y_pos, performance, align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.ylabel('articels')
        plt.xlabel('years')
        plt.title('Amount of articles')

        plt.show()



    except Exception as e:
        print(str(e))



#!/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):
    #number_of_blogs = blogs.count_documents({})
    #number_of_blogs = blogs.estimated_document_count()

    pipeline = [
        {"$group": {
            "_id": "$nick",
            "total": {"$sum": "$articles_amount"}
        }},
        {"$sort": {"total": -1}}
    ]

    cursor = blogs.aggregate(pipeline)

    result = list(cursor)

    return (result)

if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Salon
    blogs = db["Blogs"]

    try:
        results=main(blogs)
        pprint(results)
        tab=[]
        tab2=[]
        i=0
        for r in results:
            pass
            tab.append(i + 1)
            i += 1
            tab2.append(r['total'])

        print(tab, tab2)
        import matplotlib.pyplot as plt

        plt.xlabel('sorted users')
        plt.ylabel('articles amount')
        plt.plot(tab, tab2, label='line 1', linewidth=1)
        plt.show()
    except Exception as e:
        print(str(e))



#!/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):

    pipeline = [
        {"$unwind": "$articles"},
        {"$group": {
            "_id": "$blog_name",
            "views": {"$sum": "$articles.views"}
        }},
        {"$sort": {"views": -1}}
    ]

    cursor = blogs.aggregate(pipeline)

    result = list(cursor)

    pprint(result)
    #pprint(result[:10])

if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Salon24
    blogs = db["Blogs"]

    try:
        main(blogs)
    except Exception as e:
        print(str(e))



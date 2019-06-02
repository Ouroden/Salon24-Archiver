#!/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):
    number_of_blogs = blogs.count_documents({})
    #number_of_blogs = blogs.estimated_document_count()

    pipeline = [
        {"$unwind": "$articles"},
        {"$group": {
            "_id": {"title": "$articles.title", "views": "$articles.views"},
        }},
        {"$sort": {"_id.views": -1}}
    ]

    cursor = blogs.aggregate(pipeline)

    result = list(cursor)

    pprint(result)

if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Salon
    blogs = db["Blogs"]

    try:
        main(blogs)
    except Exception as e:
        print(str(e))



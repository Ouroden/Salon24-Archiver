#!/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):
    #number_of_blogs = blogs.count_documents({})
    #number_of_blogs = blogs.estimated_document_count()


    pipeline = [
        {"$project": {
            "_id": "$blog_name",
            "comments": {"$size": "$articles.comments"},
        }},
        {"$sort": {"comments": -1}}
    ]

    cursor = blogs.aggregate(pipeline)

    result = list(cursor)

    return(result)

if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Salon24
    blogs = db["Blogs"]

    try:
        results=(main(blogs))
        liczba=0
        for r in results:
            r["comments"]=int(r["comments"]*1.3)
            liczba+=r["comments"]
        print(liczba)
    except Exception as e:
        print(str(e))



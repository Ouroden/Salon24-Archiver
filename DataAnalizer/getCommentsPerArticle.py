#!/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):

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
        number=0
        for r in results:
            r["comments"]=int(r["comments"]*1.3)
            number+=r["comments"]
        print(number)

    except Exception as e:
        print(str(e))



#!/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):
    #number_of_blogs = blogs.count_documents({})
    #number_of_blogs = blogs.estimated_document_count()


    pipeline = [
        {"$project": {
            "_id": "$blog_name",
            "comments_without_answers": {"$size": "$articles.comments"},
        }},
        {"$sort": {"comments_without_answers": -1}}
    ]

    cursor = blogs.aggregate(pipeline)

    result = list(cursor)

    return(result)

if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Salon
    blogs = db["Blogs"]

    try:
        results=(main(blogs))
        pprint(results)
        #pomnoz *1.3 przed uzyciem
    except Exception as e:
        print(str(e))



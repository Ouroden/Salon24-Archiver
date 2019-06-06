#!/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):
    number_of_blogs = blogs.count_documents({})
    #number_of_blogs = blogs.estimated_document_count()

    pprint(number_of_blogs)

if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Salon24
    blogs = db["Blogs"]

    try:
        main(blogs)
    except Exception as e:
        print(str(e))



#!/usr/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):
    blog = blogs.find_one({})

    pprint(blog)


if __name__ == '__main__':
    client = MongoClient('localhost:27017')
    db = client.Blogs
    blogs = db["Blogs"]

    try:
        main(blogs)
    except Exception as e:
        print(str(e))



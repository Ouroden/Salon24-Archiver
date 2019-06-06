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
    db = client.Salon24
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

        list = [10, 20, 30, 0, 0, 0, 0, 5, 100, 0, 200, 0]
        i = 0
        length = len(tab2)
        while (i < length):
            if (tab2[i] == 0):
                tab2.remove(tab2[i])
                # as an element is removed
                # so decrease the length by 1
                length = length - 1
                # run loop again to check element
                # at same index, when item removed
                # next item will shift to the left
                continue
            i = i + 1

        tab=tab[:len(tab2)]

        import matplotlib.pyplot as plt

        plt.xlabel('sorted active users')
        plt.ylabel('articles amount')
        plt.plot(tab, tab2, label='line 1', linewidth=1)
        plt.show()
    except Exception as e:
        print(str(e))



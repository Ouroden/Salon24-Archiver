#!/bin/python

from pymongo import MongoClient
from pprint import pprint

def main(blogs):

    pipeline = [
        {"$unwind": "$articles"},
        {"$group": {
            "_id": "$articles.categories",
            "total": {"$sum": 1}
        }},
        {"$sort": {"total": -1}}
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

        tab=[0,0,0,0,0,0,0]
        for r in results:
            if(r['_id']):
                if 'Polityka' in r['_id']:
                    tab[0]+=r['total']
                if 'Gospodarka' in r['_id']:
                    tab[1] += r['total']
                if 'Rozmaitości' in r['_id']:
                    tab[2] += r['total']
                if 'Technologie' in r['_id']:
                    tab[3] += r['total']
                if 'Sport' in r['_id']:
                    tab[4] += r['total']
                if 'Społeczeństwo' in r['_id']:
                    tab[5] += r['total']
                if 'Kultura' in r['_id']:
                    tab[6] += r['total']

        print(tab)
        pprint(results)

        import matplotlib.pyplot as plt
        sizes = tab
        labels=["Polityka","Gospodarka","Rozmaitości","Technologie","Sport","Społeczeństwo","Kultura"]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.show()

    except Exception as e:
        print(str(e))



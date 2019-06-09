from pymongo import MongoClient


class DbManager:
    def __init__(self, db):
        self.db = db

    def insert_entry(self, blog):
        try:
            self.db.Blogs.insert_one(
                {
                    "nick": blog["nick"],
                    "blog_name": blog["blog_name"],
                    "blog_link": blog["blog_link"],
                    "articles": blog["articles"],
                    "followers": blog["followers"],
                    "views": blog["views"],
                    "articles_amount": blog["articles_amount"],
                    "blog_description": blog["blog_description"]
                })

        except Exception as e:
            print(str(e))

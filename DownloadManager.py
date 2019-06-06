import datetime
import urllib.request
import json
import time

def parseComments(data):
    for blog in data:
        for article in blog["articles"]:
            alink = article["article_link"]
            blink = blog["blog_link"]

            # print(alink,blink)

            article_id = (alink[len(blink):]).split(",", 1)[0]
            article["article_id"] = article_id

            for i in range(5):
                try:
                    json_url = urllib.request.urlopen(
                        'https://www.salon24.pl/comments-api/comments?sourceId=Post-' + article_id + '&sort=NEWEST&limit=100000')
                    data = json.loads(json_url.read())
                    type(data)
                    break
                except:
                    time.sleep(0.2)
                    print(i, "times try to open url")




            # print(article_id)
            for comment in data['data']["comments"]['data']:

                # print(data['data']["users"][comment['userId']]["nick"] + " : ", comment['content'])

                result = {
                    "author": data['data']["users"][comment['userId']]["nick"],
                    "content": comment['content'],
                    "votes": comment['votes'],
                    "likes": comment['likes'],
                    "dislikes": comment['dislikes'],
                    "date": datetime.datetime.fromtimestamp(
                        int(comment['created'][:-3])
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    "raw_date":int(comment['created'][:-3]),
                    "comment_id": comment['id'],
                    "replies_amount": comment['replies'],
                    "deleted": comment['deleted'],
                    "answers": []

                }
                try:
                    article["comments"].append(result)
                except:
                    print("error while adding comment")
                if (comment['replies']):

                    for answer in comment["comments"]["data"]:
                        result = {
                            "author": data['data']["users"][answer['userId']]["nick"],
                            "content": answer['content'],
                            "votes": answer['votes'],
                            "likes": answer['likes'],
                            "dislikes": answer['dislikes'],
                            "date": datetime.datetime.fromtimestamp(
                                int(answer['created'][:-3])
                            ).strftime('%Y-%m-%d %H:%M:%S'),
                            "raw_date":int(answer['created'][:-3]),
                            "comment_id": answer['id'],
                            "deleted": answer['deleted'],

                        }

                        # print(data['data']["users"][answer['userId']]["nick"] + " : ", answer['content'])
                        try:
                            article["comments"][-1]["answers"].append(result)
                        except:
                            print("error while adding answer")
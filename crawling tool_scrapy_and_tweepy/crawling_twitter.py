#!/usr/bin/env python
# encoding: utf-8

import tweepy
import json
import time
import pymongo

#mongo config
client = pymongo.MongoClient()
db = client.sisrekomwisata
table = db.wisata
table_twitter = db.wisata_twitter
wisata = table.find()

#Twitter API credentials
consumer_key = "x7XOywj3rgsSKn9MXkBNBpecr"
consumer_secret = "o4lHJPQQyVGQaojTGPTHR9BOXuEzvRzbghBkPMrAyaBoPRQjvd"
access_key = "3994061302-XFnBADeFR4WBxZzmXAy4sXn2sSHu6aYldjZgbVk"
access_secret = "g4FCmePHacsvv7nJOp2sJRaY9nbnH556s97whuOKILFrI"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

#Put your search term
no = 0
for i in wisata:
    no += 1
    searchquery = i['nama']

    users =tweepy.Cursor(api.search,q=searchquery).items()
    count = 0
    errorCount=0
    if no > 92:
        print(no,i['nama'])
        while True:
            try:
                user = next(users)
                count += 1
                if (count>1500):
                    break
            except tweepy.TweepError:
                print("sleeping....")
                time.sleep(60*16)
                user = next(users)
            except StopIteration:
                break
            try:
                print(user.text)
                wisata_tweet = {
                                'id_wisata': i['_id'],
                                'text': user.text
                                }
                table_twitter.insert_one(wisata_tweet)
            
            except UnicodeEncodeError:
                errorCount += 1
                print("UnicodeEncodeError,errorCount ="+str(errorCount))

        print("completed, errorCount ="+str(errorCount)+" total tweets="+str(count))


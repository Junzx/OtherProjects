# -*- coding: UTF-8 –*-
import pymongo

client  = pymongo.MongoClient("localhost", 27017)

db = client ['testdb']

newcollection = db['newcollection']
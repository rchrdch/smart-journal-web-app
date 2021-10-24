# DATABASE CONFIGURATION

from flask import Flask
from flask_pymongo import pymongo
import pymongo

CONNECTION_STRING = ""

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('smart-journal-db')
# user_collection = pymongo.collection.Collection(db, 'user_collection')


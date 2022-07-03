from dotenv import load_dotenv
from os.path import join, dirname
import os
from pymongo import MongoClient
import pymongo 


dotenv_path = join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
cnxn = os.environ.get('CNXN')

db = MongoClient(cnxn).surface
urlsTable = db.urls
statusTable = db.status

urlsTable.drop()
statusTable.drop()
statusTable.insert_one({"depth":0})
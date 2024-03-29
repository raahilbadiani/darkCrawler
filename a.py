import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
from os.path import join, dirname
import os
from pymongo import MongoClient
import sys
from urllib.parse import urlparse,urljoin

dotenv_path = join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
cnxn = os.environ.get('CNXN')
firstTime = os.environ.get('FIRSTTIME')

db = MongoClient(cnxn).surface
urlsTable = db.urls
statusTable = db.status

session = requests.session()
# session.proxies["http"] = "socks5h://localhost:9001"
# session.proxies["https"] = "socks5h://localhost:9001"

active = [] # contains all urls 
visited = {} # contains domain names already visited 
routes = {} # contains different routes for a particular url we can visit 
activeAdded = {}

domainVisCount = 0
depth = 0
curLevelVisCnt = 0
noOfRoutesPerDomain = 10

def generate_seeds():
    obj1 = {"domain":"amazon.com","routeVisCount":0,"routes":[""],"depth":0}
    obj2 = {"domain":"google.com","routeVisCount":0,"routes":[""],"depth":0}
    urlsTable.insert_many([obj1,obj2])

def get_top_urls(n):
    # modify it later to get top n websites from database. 
    # url = "darkzzx4avcsuofgfez5zq75cqc4mprjvfqywo45dfcaxrwqg6qrlfid.onion"
    # url = ["paavlaytlfsqyvkg3yqj7hflfg5jw2jdg2fgkza5ruf6lplwseeqtvyd.onion","55niksbd22qqaedkw36qw4cpofmbxdtbwonxam7ov2ga62zqbhgty3yd.onion"]
    curDepth = list(statusTable.find())[0]['depth']
    print(f'depth = {curDepth}')
    urlObjs = list(urlsTable.find({"depth":curDepth}).sort('routeVisCount').limit(n))
    print(f'urls -> {urlObjs}')
    return urlObjs

def parse_page(parUrl,parDepth):        
    try:
        response = session.get(parUrl)
        soup = BeautifulSoup(response.content, "html.parser")
        
        for link in soup.find_all("a"):
            url = urlparse(link.get("href"))
            curDomain = url.hostname
            curRoute = url.path
            if curDomain == None or curDomain == '':
                curDomain = urlparse(parUrl).hostname
            if curRoute == '/':
                curRoute = ''
            updates = {
                "$addToSet": {
                    "routes":{
                        "$each":["",curRoute]
                    },
                },
                "$setOnInsert":{
                    "routeVisCount":0,
                    "depth":parDepth+1
                }                    
            }
            # check if curDomain in urls_table 
            # if not then insert it and make routes = ["",curRoute], and also set routeVisCount to 0, depth=parDepth+1
            # if it already exists then append "" and curRoute to routes if they are not already in there and dont change the value of routeVisCount
            
            urlsTable.find_one_and_update({"domain":curDomain},updates,upsert=True)
    except:
        print(f'[-] Could not visit {parUrl}')


if firstTime=="1":
    generate_seeds()

while True:
    try:
        seeds = get_top_urls(50)
        print(f'seeds -> {[s["domain"] for s in seeds]}')
        for seed in seeds:
            routeVisCountCur = 0
            domain = seed["domain"]
            routes = seed["routes"]
            routeVisCount = seed["routeVisCount"]
            n = len(routes)
            domainVisCount += 1
            print(f'...............domains visited = {domainVisCount}............')
            for i in range(routeVisCount,min(n,routeVisCount+noOfRoutesPerDomain)):
                routeVisCountCur+=1
                if routeVisCountCur > noOfRoutesPerDomain:
                    break # to not overvisit same website and also give others a chance
                    # change this later to make it dyanmic
                url = urljoin("http://"+domain,routes[i])
                print(f'url = {url}')
                parse_page(url,depth)

            # update routeVisCount of parUrl now since we have visited its few children
            updates = {
                "$inc":{
                    "routeVisCount":routeVisCountCur
                }
            }
            urlsTable.find_one_and_update({"domain":domain},updates)
        curLevelVisCnt += len(seeds)
        if curLevelVisCnt >= urlsTable.count_documents({"depth":depth}):
            curLevelVisCnt = 0
            depth += 1
            statusTable.find_one_and_update({"depth":depth-1},{"$set":{"depth":depth}})
            print('[+] updating status table moving to next level')
    except KeyboardInterrupt as k:
        sys.exit()

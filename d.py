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

db = MongoClient(cnxn).dark
urlsTable = db.urls
statusTable = db.status

session = requests.session()
session.proxies["http"] = "socks5h://localhost:9050"
session.proxies["https"] = "socks5h://localhost:9050"

active = [] # contains all urls 
visited = {} # contains domain names already visited 
routes = {} # contains different routes for a particular url we can visit 
activeAdded = {}

domainVisCount = 0
depth = 0
curLevelVisCnt = 0
noOfRoutesPerDomain = 10

def generate_seeds():
    objs = [
        {"domain":"darkzzx4avcsuofgfez5zq75cqc4mprjvfqywo45dfcaxrwqg6qrlfid.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"paavlaytlfsqyvkg3yqj7hflfg5jw2jdg2fgkza5ruf6lplwseeqtvyd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion","routeVisCount":0,"routes":["","wiki"],"depth":0},
        {"domain":"juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"p53lf57qovyuvwsc6xnrppyply3vtqm7l6pcobkmyqsiofyeznfu5uqd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"archiveiya74codqgiix​o33q62qlrqtkgmcitqx5​u2oeqnmn5bpcbiyd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"www.nytimes3xbfgragh.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"www.bbcnewsd73hkzno2ini43t4gblxvycyac5aw4gnv7t2rccijh7745uqd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"www.facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"ciadotgov4sjwlzihbbgxnqg3xiyrg7so2r2o3lt5wz5ypk4sxyjstad.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"wasabiukrxmkdgve5kynjztuovbg43uxcbcxn6y2okcrsg7gb6jdmbad.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"keybase5wmilwokqirssclfnsqrjdsi7jdir5wy7y7iu3tanwmtp6oid.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"zerobinftagjpeeebbvyzjcqyjpmjvynj5qlexwyxe7l3vqejxnqv5qd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"sdolvtfhatvsysc6l34d65ymdwxcujausv7k5jk4cy5ttzhjoi6fzvyd.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"crqkllx7afomrokwx6f2sjcnl2do2i3i77hjjb4eqetlgq3cths3o6ad.onion","routeVisCount":0,"routes":[""],"depth":0},
        {"domain":"privacy2zbidut4m4jyj3ksdqidzkw3uoip2vhvhbvwxbqux5xy5obyd.onion","routeVisCount":0,"routes":[""],"depth":0}
    ]

    urlsTable.insert_many(objs)

def get_top_urls(n):
    # modify it later to get top n websites from database. 
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
            if "onion" not in curDomain:
                continue
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

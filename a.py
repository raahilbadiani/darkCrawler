import requests
from bs4 import BeautifulSoup
import re

session = requests.session()
session.proxies["http"] = "socks5h://localhost:9050"
session.proxies["https"] = "socks5h://localhost:9050"

active = [] # contains all urls 
visited = {} # contains domain names already visited 
routes = {} # contains different routes for a particular url we can visit 
count = 0
activeAdded = {}

def getSeeds():
    # modify it later to get seeds from database using better techniques
    url = "darkzzx4avcsuofgfez5zq75cqc4mprjvfqywo45dfcaxrwqg6qrlfid.onion"
    return [url]


def getUrls(parUrl):
    global active, visited, routes, activeAdded, count

    if parUrl in visited:
        return # already visited domain hence ignore

    visited[parUrl] = True # marking visitd flag to true

    if parUrl not in routes:
        routes[parUrl] = [''] # initialize as list with empty string i.e '/' route


    count += 1
    print(f'...............domains visited = {count}............')
    routeCnt = 0
    print(f'Domain: {parUrl}')


    for route in routes[parUrl]:
        routeCnt+=1
        if routeCnt > 10:
            break # to not overvisit same website and also give others a chance
            # change this later to make it dyanmic

        print(f'{routeCnt}; {route=}')
        
        try:
            fullPath = f'{parUrl}/{route}'
            response = session.get(fullPath)
            soup = BeautifulSoup(response.content, "html.parser")


            for link in soup.find_all("a"):
                url = link.get("href")
                url = re.sub("#.*","",url) # remove # symbol
                url = re.sub(".*http(s?)://","",url) # remove http/https from url 
                urlSplitted = re.split('/',url) # separate domain and route
                curDomain = urlSplitted[0] # domain name
                curRoutes = '/'.join(urlSplitted[1:]) # route
               

                if  curDomain != '' and curDomain not in activeAdded: 
                    activeAdded[curDomain] = True # means we have hit it once
                    active.append(curDomain)
                if curRoutes != '':
                    routes[parUrl].append(curRoutes)
                # print(f'{url=}; {curRoutes=}')


        except:
            print(f'[-] Could not visit {parUrl}')

active = getSeeds()

for url in active:
    url = "http://"+url
    getUrls(url)

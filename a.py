import requests
from bs4 import BeautifulSoup

session = requests.session()
session.proxies["http"] = "socks5h://localhost:9050"
session.proxies["https"] = "socks5h://localhost:9050"

active = [] # contains urls yet to be visited 
visited = {} # contains urls already visited 
routes = {} # contains different routes for a particular url we can visit 

def getSeeds():
    # modify it later to get seeds from database using better techniques
    url = "http://darkzzx4avcsuofgfez5zq75cqc4mprjvfqywo45dfcaxrwqg6qrlfid.onion/"
    return [url]


def getUrls(parUrl):
    global active, visited, routes

    if parUrl in visited:
        return

    if parUrl not in routes:
        routes[parUrl] = []
    
    response = session.get(parUrl)
    soup = BeautifulSoup(response.content, "html.parser")

    visited[parUrl] = True

    print(f'printing urls for {parUrl}')
    for link in soup.find_all("a"):
        url = link.get("href")
        if link.get("href").startswith("/"):
            # /routes of the same domain
            # also right now not checking unique routes to be done when storing in database
            routes[parUrl].append(url)
        else:
            # new domains
            # extract domain from this !!
            print(url)
            if url not in visited:
                active.append(url)

active = getSeeds()

for url in active:
    getUrls(url)
    # print(urls)

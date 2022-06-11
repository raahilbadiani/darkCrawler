import requests
from bs4 import BeautifulSoup

session = requests.session()
session.proxies["http"] = "socks5h://localhost:9050"
session.proxies["https"] = "socks5h://localhost:9050"

active = [] # contains urls yet to be visited 
visited = {} # contains urls already visited 
routes = {} # contains different routes for a particular url we can visit 

url = 'http://dv3pmqy5uw26jv5tsu6n457aswf4wmumez5kjjowuuev5rl33rsq.b32.i2p/'


try:
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")


    for link in soup.find_all("a"):
        url = link.get("href")
        if link.get("href").startswith("/"):
            # /routes of the same domain
            # also right now not checking unique routes to be done when storing in database
            pass
        else:
            # new domains
            # extract domain from this !!
            print(url)
except:
    print('error occured')


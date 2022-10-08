import requests
from bs4 import BeautifulSoup as bs
from time import sleep

def fromLink(url,key, js = False):
    """ Searches URL for <a> links that include the keyword ```key```.
    \nif ```js``` is True, load page and get source with selenium """
    import util.openFromLinks as openFromLinks

    if js == True:
        web = False
        driver = openFromLinks.runWeb(web)
        driver.get(url)
        sleep(1)
        data = driver.page_source
    else:
        # set vars
        URL = url
        keyword = key
        # ^^change these

        # get html
        data = requests.get(URL).content

    # set soup
    soup = bs(data, 'html.parser')

    # create empty list
    links = []

    # populate list
    for link in soup.find_all('a'):
        if link is not None:
                if key in link:
                    links.append(link.get('href'))
    return links
 
def fromFile(file,key):
    """returns links from html file"""
    # optional: read from file
    fLinks = []
    data = open(file,"r", encoding="utf8").read()
    #data = text.read()
    soup = bs(data, 'html.parser')
    for link in soup.find_all('a'):
        if link is not None:
            if key in link.get('href'):
                fLinks.append(link.get('href'))

    return fLinks

def writeLinks(links):
    """write list::change filename if necessary"""
    with open("text/flinks.txt", "w") as l:
        for link in links:
            l.write(f"{link}\n")


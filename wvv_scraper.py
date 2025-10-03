import cloudscraper
from bs4 import BeautifulSoup

def scrape_wvv(urls):
    for url in urls:
        pass
    # find all tabs in each url
    # store BID37126 in # smthg
    # get data from https://www.volleyball-wien.at/index.php?option=com_oevv&view=oevv&ShowTab=1&ShowErg=1&Style=Standard&BID=37391
    
    
def getAllTeamNames_wvv(url):
    matches = getMatchList(url)
    results = set()
    global base_url
    for match in matches:
        # Extract team names
        team_names = match.find_all("div", class_="name")
        for t in team_names:
            results.add(t.text)
    return list(results)
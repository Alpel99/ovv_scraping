from bs4 import BeautifulSoup
import time, random
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
from ovv_scraper import scrape_ovv, getAllTeamNames_ovv
from wvv_scraper import scrape_wvv
from gendata import genICS, genJSON

# === CONFIGURATION ===
BL = False
LL = True
URL_OVV = "https://panel.volleystation.com/website/125/de/schedule/"
# URLS_WVV = ["https://www.volleyball-wien.at/tabellen/herren.html", "https://www.volleyball-wien.at/tabellen/damen.html", "https://www.volleyball-wien.at/tabellen/nachwuchs-burschen.html", "https://www.volleyball-wien.at/tabellen/nachwuchs-maedchen.html"]
URLS_WVV = "https://www.volleyball-wien.at/termine-ergebnisse.html"
TARGET_TEAMS = []

if __name__ == "__main__":
    # print(getAllTeamNames_ovv(URL_OVV))
    data = []
    if(BL):
       res_bl = scrape_ovv(URL_OVV, TARGET_TEAMS)
       if(res_bl):
            data.extend(res_bl)
    if(LL):
        res_ll = scrape_wvv(URLS_WVV, TARGET_TEAMS)
        if(res_ll):
            data.extend(res_ll)
    print("[ALL] found ", len(data), "games with ", TARGET_TEAMS)
    for e in data:
        print(e)

    # genICS(data)
    path = "../frontend/schedule.json"
    genJSON(data, path)
    
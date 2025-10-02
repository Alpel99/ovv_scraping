from bs4 import BeautifulSoup
import time, random
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
from ovv_scraper import scrape_ovv
from wvv_scraper import scrape_wvv

# === CONFIGURATION ===
BL = True
LL = False
URL_OVV = "https://www.volleynet.at/2-bundesliga-herren/"
URLS_WVV = ["https://www.volleyball-wien.at/tabellen/herren.html", "https://www.volleyball-wien.at/tabellen/damen.html", "https://www.volleyball-wien.at/tabellen/nachwuchs-burschen.html", "https://www.volleyball-wien.at/tabellen/nachwuchs-maedchen.html"]

TARGET_TEAM = "Union VV Döbling"

if __name__ == "__main__":
    if(BL):
        scrape_ovv(URL_OVV)
    if(LL):
        scrape_wvv(URLS_WVV)
    print("hello")
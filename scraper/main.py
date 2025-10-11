from ovv_scraper import scrape_ovv
from wvv_scraper import scrape_wvv
from gendata import genICS, genJSON

# links
URL_HBL2 = "https://panel.volleystation.com/website/125/de/schedule/"
URL_DBL2 = "https://panel.volleystation.com/website/118/de/schedule/"
URL_DBL = "https://panel.volleystation.com/website/121/de/schedule/"
URL_HBL = "https://panel.volleystation.com/website/122/de/schedule/"
URL_HBCUP = "https://panel.volleystation.com/website/123/de/schedule/"
URL_DBCUP = "https://panel.volleystation.com/website/119/de/schedule/"
URL_WVV = "https://www.volleyball-wien.at/termine-ergebnisse.html"

if __name__ == "__main__":
    print("Running scraper...")
    data = []

    data.extend(scrape_ovv(URL_HBL2, "HBL2"))
    data.extend(scrape_ovv(URL_HBCUP, "HBCUP"))
    data.extend(scrape_ovv(URL_HBL, "HBL"))

    data.extend(scrape_ovv(URL_DBL2, "DBL2"))
    data.extend(scrape_ovv(URL_DBL, "DBL"))
    data.extend(scrape_ovv(URL_DBCUP, "DBCUP"))
    print("[OVV] found ", len(data), "matches")

    data.extend(scrape_wvv(URL_WVV))
    print("[ALL] found ", len(data))

    path = "frontend/schedule.json"
    # genICS(data)
    genJSON(data, path)
    
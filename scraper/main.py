from ovv_scraper import scrape_ovv
from wvv_scraper import scrape_wvv
from gendata import genICS, genJSON

# links
URL_OVV = "https://panel.volleystation.com/website/125/de/schedule/"
URL_WVV = "https://www.volleyball-wien.at/termine-ergebnisse.html"

if __name__ == "__main__":
    data = []

    data.extend(scrape_ovv(URL_OVV))

    data.extend(scrape_wvv(URL_WVV))
    
    print("[ALL] found ", len(data))
    
    # for e in data:
        # print(e)

    # genICS(data)
    
    path = "frontend/schedule.json"

    genJSON(data, path)
    
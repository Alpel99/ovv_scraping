import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from matchdate import matchdate

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/118.0.5993.117 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

def findCompetitions2(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    select = soup.find("select", class_="BewerbPullDown")
    comps = []
    for comp in select.find_all("option"):
        value = comp.get("value")
        text = comp.text.strip()
        comps.append([text, value])
    return comps

def getCompMatches(comp):
    (compName, compID) = comp
    url = f"https://www.volleyball-wien.at/index.php?option=com_oevv&view=oevv&Style=Standard&BID={compID}"
    # print("scraping", compName, compID, "url:", url)
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for tr in soup.find_all("tr"):
        # print("new tr", tr)
        classes = tr.get("class", [])
        
        # skip header of table (class CH, red)
        if "CH" in classes:
            continue

        # skip rows that don't look like match rows (no match number cell)
        spn_td = tr.find("td", class_="ErgSpN")
        if spn_td is None:
            continue

        # Check ErgSet presence / content
        ergset_td = tr.find("td", class_="ErgSet")
        ergset_text = ergset_td.get_text(strip=True) if ergset_td else ""
        # If ErgSet has text -> match played -> skip
        if ergset_text:
            continue
        
        def text_of(cls):
            td = tr.find("td", class_=cls)
            return td.get_text(strip=True) if td else None
        
        location = text_of("ErgHalle")
        link = url
        dateT = text_of("ErgDat") + " " + text_of("ErgZeit")  # format e.g. "27.09.2025" + " " + "15:00"
        home = text_of("ErgHeim")
        guest =  text_of("ErgGast")        

        dt = datetime.strptime(dateT, "%d.%m.%Y %H:%M")
        md = matchdate(home, guest, dt, location, link, compName)
        results.append(md)

    print("Found", len(results), "matches for", compName)
    return results

def scrape_wvv(url):
    data = []
    # find all tabs in each url
    comps = findCompetitions2(url)
    for comp in comps:
        res = getCompMatches(comp)
        data.extend(res)
    print("[WVV] found ", len(data), "matches")
    return data
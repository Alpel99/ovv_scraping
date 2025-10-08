import cloudscraper
from bs4 import BeautifulSoup
from matchdate import matchdate
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def findCompetitions(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    ul = soup.find("ul", id="BewerbslisteTabs")
    tabs = [(a.get_text(strip=True), a["href"].lstrip('#BID')) for a in ul.find_all("a", href=True)]

    return tabs

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


def getCompMatches(comp, targets):
    (compName, compID) = comp
    url = f"https://www.volleyball-wien.at/index.php?option=com_oevv&view=oevv&Style=Standard&BID={compID}"
    # print("scraping", compName, compID, "url:", url)
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for tr in soup.find_all("tr"):
        classes = tr.get("class", [])
        if "CH" in classes:
            continue  # skip rows with class "CH"

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

        if(targets):
            if not any(x in targets for x in [text_of("ErgHeim"), text_of("ErgGast")]):
                continue
        

        dt = datetime.strptime(dateT, "%d.%m.%Y %H:%M")
        md = matchdate(home, guest, dt, location, link, compName)
        results.append(md)

    print("Found", len(results), "matches for", compName)
    return results

def scrape_wvv(url, targets):
    data = []
    # find all tabs in each url
    # store BID37126 in # smthg
    comps = findCompetitions2(url)
    print("comps: ", comps)
    for comp in comps:
        res = getCompMatches(comp, targets)
        data.extend(res)

    return data

# don't need
def getAllTeamNames_wvv(url):
    matches = findCompetitions(url)
    results = set()
    global base_url
    for match in matches:
        # Extract team names
        team_names = match.find_all("div", class_="name")
        for t in team_names:
            results.add(t.text)
    return list(results)
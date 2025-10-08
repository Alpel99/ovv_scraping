import cloudscraper
from bs4 import BeautifulSoup
from matchdate import matchdate

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/118.0.5993.117 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

GERMAN_MONTH_TO_NUM = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}

def getMatchList(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    matches = soup.find_all("a", class_="table-row")
    return matches

def filterMatches(matches, base_url):
    results = []
    for match in matches:
        href = match.get("href")
        full_link = base_url + href
        results.append(full_link)
    return results
    
def scrapeMatches(filteredMatchLinks):
    from datetime import datetime
    import time, random
    results = []
    for i, link in enumerate(filteredMatchLinks, start=1):
        if i % max(1, len(filteredMatchLinks) // 10) == 0 or i == len(filteredMatchLinks):
            print(f"Processing: {i}/{len(filteredMatchLinks)}")
        scraper = cloudscraper.create_scraper()
        response = scraper.get(link,  headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        # print(link)
        
        date_block = soup.find("div", class_="details date")
        names = soup.find_all("div", class_="name")
                   
        parts = date_block.get_text(" ", strip=True).split(',')
        round = parts[0].strip()
        location = parts[1].strip()
        # dateT = parts[-2].strip() + ", " + parts[-1].strip()
        dateP = parts[-2].strip().split(' ')
        dateT = dateP[0] + " " + str(GERMAN_MONTH_TO_NUM[dateP[1]]) + " " + dateP[2] + ", " + parts[-1].strip()
        
        home = names[0].get_text() 
        guest = names[1].get_text() 
            
        dt = datetime.strptime(dateT, "%d %m %Y, %H:%M")
        md = matchdate(home, guest, dt, location, link, "BL2")
        # print("Found match", md)
        results.append(md)
        time.sleep(random.uniform(3,7))   
    return results
        
        

def scrape_ovv(url):
    # BASE_URL = "panel.volleystation.com"  # Will be prepended to relative links
    base_url = "/".join(url.split("/", 3)[:3])
    matches = getMatchList(url)
    filteredMatchLinks = filterMatches(matches, base_url)
    print("[OVV] found ", len(filteredMatchLinks), "matches")
    matchdata = scrapeMatches(filteredMatchLinks)
    # matchdata = scrapeMatches(filteredMatchLinks[:5])

    print("[OVV] scraped ", len(filteredMatchLinks), "matches")
    return matchdata



import cloudscraper
from bs4 import BeautifulSoup
from matchdate import matchdate

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
    import locale, time, random
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    results = []
    for link in filteredMatchLinks:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(link)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        print(link)
        date_block = soup.find("div", class_="details date")
        names = soup.find_all("div", class_="name")
        
        parts = date_block.get_text(" ", strip=True).split(',')
        round = parts[0].strip()
        location = parts[1].strip()
        dateT = parts[-2].strip() + ", " + parts[-1].strip()
        
        home = names[0].get_text() 
        guest = names[1].get_text() 
            
        dt = datetime.strptime(dateT, "%d %B %Y, %H:%M")
        md = matchdate(home, guest, dt, location, link, "BL2")
        # print("Found match", md)
        results.append(md)
        time.sleep(random.uniform(2,5))   
    return results
        
        

def scrape_ovv(url):
    # BASE_URL = "panel.volleystation.com"  # Will be prepended to relative links
    base_url = "/".join(url.split("/", 3)[:3])
    matches = getMatchList(url)
    filteredMatchLinks = filterMatches(matches, base_url)
    print("[OVV] found ", len(filteredMatchLinks), "games")
    matchdata = scrapeMatches(filteredMatchLinks)
    return matchdata



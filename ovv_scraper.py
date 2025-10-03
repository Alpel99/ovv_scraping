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

def filterMatches(matches, targets, base_url):
    results = []
    for match in matches:
        # Extract team names
        team_names = match.find_all("div", class_="name")
        teams = [t.get_text(strip=True) for t in team_names]
        # Check if TARGET_TEAM is involved
        if any(x in targets for x in teams):
            href = match.get("href")
            full_link = base_url + href
            results.append(full_link)
    return results
    
def scrapeMatches(filteredMatchLinks, targets):
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
        
        if(len(targets) == 1):
            home = names[0].get_text() in targets
            opponent = names[0].get_text() if not home else names[1].get_text()
            title = "Heimspiel" if home else "Auswärtsspiel"
            title += " vs " + opponent + ", " + round
        else:
            title = names[0].get_text() + " vs " + names[1].get_text() + ", " + round
            
        dt = datetime.strptime(dateT, "%d %B %Y, %H:%M")
        md = matchdate(title, dt, location, link)
        print("Found match", md)
        results.append(md)
        time.sleep(random.uniform(3,7))   
    return results
        
        

def scrape_ovv(url, targets):
    # BASE_URL = "panel.volleystation.com"  # Will be prepended to relative links
    base_url = "/".join(url.split("/", 3)[:3])
    print(base_url)
    matches = getMatchList(url)
    filteredMatchLinks = filterMatches(matches, targets, base_url)
    print("[OVV] found ", len(filteredMatchLinks), "games with ", targets)
    matchdata = scrapeMatches(filteredMatchLinks, targets)
    return matchdata
    
    
def getAllTeamNames_ovv(url):
    matches = getMatchList(url)
    results = set()
    global base_url
    for match in matches:
        # Extract team names
        team_names = match.find_all("div", class_="name")
        for t in team_names:
            results.add(t.text)
    return list(results)



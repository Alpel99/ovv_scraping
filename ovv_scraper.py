import cloudscraper
from bs4 import BeautifulSoup

def getMatchList(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    html = response.text
    html = str(html)
    soup = BeautifulSoup(html, "html.parser")
    # print(repr(response[:500]))

    iframe_tag = soup.find("iframe", class_="shortcode_iframe oevv-iframe")
    iframe_url = iframe_tag["src"]
    # print(iframe_url)

    # all_links = soup.find_all("a")
    # print("Found links:", len(all_links))
    # print("Found links:", all_links)



    # for a in soup.find_all("a"):#, class_="quick-links-item"):
    #     span = a.find("span")
    #     if span: print(span.get_text())
    #     if span and "Spiele" in span.get_text(strip=True):
    #         print(a["href"])
    #         break

    # a = soup.select_one("a.quick-links-item panel-1")
    # print(soup.prettify()[:2000])
    # print(a)

    # all of this is fucked
    return "https://panel.volleystation.com/website/125/de/schedule/"

def scrape_ovv(url):
    BASE_URL = "panel.volleystation.com"  # Will be prepended to relative links
    getMatchList(url)



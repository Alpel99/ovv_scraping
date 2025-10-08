import urllib.request
from bs4 import BeautifulSoup
import time, random
import locale
# Let's set a german locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')

# === CONFIGURATION ===
URL = "https://panel.volleystation.com/website/125/de/schedule/"  # <-- Replace with actual match schedule URL
TARGET_TEAM = "Union VV Döbling"
BASE_URL = "panel.volleystation.com"  # Will be prepended to relative links


# === FETCH PAGE ===
html = req(URL)
# html = urllib.request.urlopen(req).read().decode('utf-8')

# === PARSE HTML WITH BEAUTIFULSOUP ===
soup = BeautifulSoup(html, "html.parser")

# Find all match entries (<a class="table-row">)
matches = soup.find_all("a", class_="table-row")

results = []

for match in matches:
    # Extract team names
    team_names = match.find_all("div", class_="name")
    teams = [t.get_text(strip=True) for t in team_names]

    # Check if TARGET_TEAM is involved
    if TARGET_TEAM in teams:
        href = match.get("href")
        print("Test: ", href.startswith("http"))
        full_link = href if href.startswith("http") else BASE_URL + href
        results.append("https://"+full_link)

# === OUTPUT ===
if results:
    print("Gefundene Spiele mit", TARGET_TEAM, ":", len(results))
    # for link in results:
    #     print(link)
else:
    print("Keine Spiele gefunden für:", TARGET_TEAM)
    

def make_ics_event(start, title, location, link, early_hours = 1.5, duration_hours=2):
    # Calculate DTEND as start + duration
    from datetime import datetime, timedelta
    dt = datetime.strptime(start, "%d %B %Y, %H:%M")
    dtstart = dt - timedelta(hours=early_hours)
    dtend = dt + timedelta(hours=duration_hours)

    return (
        "BEGIN:VEVENT\n"
        f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')}\n"
        f"DTEND:{dtend.strftime('%Y%m%dT%H%M%S')}\n"
        f"SUMMARY:{title}\n"
        f"LOCATION:{location}\n"
        f"DESCRIPTION:Match Link: {link}\n"
        "END:VEVENT\n"
    )

ics_events = []

for link in results:
    # try:
        # Build request again with headers
        req = urllib.request.Request(link)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
        req.add_header('Accept-Language', 'de-DE,de;q=0.9,en;q=0.5')

        html = urllib.request.urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        # Find the date block
        date_block = soup.find("div", class_="details date")
        names = soup.find_all("div", class_="name")
        home = names[0].get_text() == "Union VV Döbling"
        gegner = names[0].get_text() if not home else names[1].get_text()

        if date_block:
            # Clean text around comma before <span>
            parts = date_block.get_text(" ", strip=True).split(',')
            runde = parts[0].strip()
            ort = parts[1].strip()
            datum_zeit = parts[-2].strip() + ", " + parts[-1].strip()
            
            titel = "Heimspiel VVD" if home else "Auswärtsspiel VVD"
            titel += " vs " + gegner + ", " + runde
            # After extracting:
            print(f"\nLink: {link}")
            print("Spiel:", titel)
            print("Ort:", titel)
            print("Datum/Zeit:", datum_zeit)

            vevent = make_ics_event(datum_zeit, titel, ort, link)
            ics_events.append(vevent)
            
        else:
            print(f"\nLink: {link}")
            print("Kein Datum gefunden!")
            
            
        time.sleep(random.uniform(2, 5))

    # except Exception as e:
    #     print(f"\nFehler bei {link}: {e}")


# Final write
with open("schedule_vvd.ics", "w", encoding="utf-8") as f:
    f.write("BEGIN:VCALENDAR\nVERSION:2.0\n")
    f.write("PRODID:oevv-events-doebling\n")
    for event in ics_events:
        f.write(event)
    f.write("END:VCALENDAR")



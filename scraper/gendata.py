import json

def genICS(events):
    with open("schedule.ics", "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\n")
        f.write("PRODID:oevv-events-doebling\n")
        for event in events:
            f.write(event.make_ics_event())
        f.write("END:VCALENDAR")

def genJSON(events, path):
    from datetime import datetime
    data = []
    for event in events:
        data.append(event.make_json_event())
    
    jdata = {"lastScrape": datetime.now().isoformat(),
             "matches": data}

    with open(path, "w", encoding="utf-8") as f:
        json.dump(jdata, f, ensure_ascii=False, indent=2)
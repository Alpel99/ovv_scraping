import matchdate

def genICS(events):
    with open("schedule.ics", "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\nVERSION:2.0\n")
        f.write("PRODID:oevv-events-doebling\n")
        for event in events:
            f.write(event.make_ics_event())
        f.write("END:VCALENDAR")
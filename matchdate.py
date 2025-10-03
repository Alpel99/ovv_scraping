from datetime import datetime, timedelta


class matchdate:
    def __init__(self, title, dateT: datetime, location, link=None, duration=timedelta(hours=1.5), early=timedelta(hours=1.5)):
        self.title = title
        self.location = location
        self.dateT = dateT
        self.link = link
        self.duration=duration
        self.early = early
        
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Event(title={self.title!r}, dateT={datetime.strftime(self.dateT, '%d %B %Y, %H:%M')!r}, location={self.location!r})"

    def make_ics_event(self):
        return (
            "BEGIN:VEVENT\n"
            f"DTSTART:{(self.dateT-self.early).strftime('%Y%m%dT%H%M%S')}\n"
            f"DTEND:{(self.dateT+self.duration).strftime('%Y%m%dT%H%M%S')}\n"
            f"SUMMARY:{self.title}\n"
            f"LOCATION:{self.location}\n"
            f"DESCRIPTION:Match Link: {self.link}\n"
            "END:VEVENT\n"
        )
            
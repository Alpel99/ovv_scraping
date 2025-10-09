// script.js
// Pure JS frontend: loads schedule.json (or fallback sample), allows adding filters,
// runs unioned filtering, displays unique results in table + FullCalendar,
// and exports JSON / ICS.

// CONFIG
const DATA_URL = "schedule.json"; // place your scraped JSON here or it will fallback to sample
const teamsListEl = document.querySelector("#teamsList");
const teamInput = document.querySelector("#teamInput");
const leagueSelect = document.querySelector("#leagueSelect");
const startDateInput = document.querySelector("#startDate");
const addFilterBtn = document.querySelector("#addFilterBtn");
const filtersListEl = document.querySelector("#filtersList");
const runFiltersBtn = document.querySelector("#runFiltersBtn");
const resultsTableBody = document.querySelector("#resultsTable tbody");
const resultsCount = document.querySelector("#resultsCount");
const downloadIcsBtn = document.querySelector("#downloadIcsBtn");
const defaultDurationInput = document.querySelector("#defaultDuration");

let DATA = [];      // loaded dataset
let FILTERS = [];   // array of {team, league, startDate}
let FILTERED = [];  // results after run

// helper: parse ISO string robustly
function toDate(iso) {
  return new Date(iso);
}

// human friendly date
function formatLocal(dt) {
  if (!dt) return "";
  const d = new Date(dt);
  return d.toLocaleString();
}

// download helper
function download(filename, content, mime = "application/octet-stream") {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// load schedule.json or fallback
async function loadData() {
  try {
    const res = await fetch(DATA_URL);
    if (!res.ok) throw new Error("no local data or CORS");
    DATA = await res.json();
    console.log("Loaded schedule.json, length:", DATA.length);
  } catch (e) {
    console.warn("Could not load schedule.json, using sample data. Error:", e.message);
    DATA = sampleData();
  }
  populateTeamLeagueLists();
}

// sample fallback (very small)
function sampleData() {
  return {
    "lastScrape": "2025-10-09T11:45:00",
    "matches": [
    { "title": "UVC RAIBA Waidhofen/Ybbs vs Volleyteam Roadrunners Wien, Runde 2", "location": "SH {WAIDHOFEN/YBBS}", "dateT": "2025-10-10T20:00:00", "link": "https://panel.volleystation.com/website/125/de/matches/2241158/", "league": "BL2" },
    { "title": "HLL: Dimitrios 1 vs VTR 2", "location": "Sporthalle Brigittenau", "dateT": "2025-10-26T14:30:00", "link": "https://www.volleyball-wien.at/index.php?option=com_oevv&view=oevv&Style=Standard&BID=36629", "league": "HLL" }
  ]
  };
}

// populate team datalist and league select
function populateTeamLeagueLists() {
  if (DATA.lastScrape) {
    console.log("Last scraped:", DATA.lastScrape);
    const lastScrapeEl = document.getElementById("lastScraped");
        const scrapeDate = new Date(DATA.lastScrape);
        lastScrapeEl.textContent = "Last scraped: " + scrapeDate.toLocaleString("de-DE", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
  }
  const teams = new Set();
  const leagues = new Set();
  DATA.matches.forEach(item => {
    if (item.home) teams.add(item.home);
    if (item.guest) teams.add(item.guest)
    if (item.league) leagues.add(item.league);
  });

  // fill datalist
  teamsListEl.innerHTML = "";
  Array.from(teams).sort().forEach(t => {
    const opt = document.createElement("option");
    opt.value = t;
    teamsListEl.appendChild(opt);
  });

  // fill league select (keep Any)
  const existing = new Set(Array.from(leagueSelect.options).map(o => o.value));
  Array.from(leagues).sort().forEach(l => {
    if (!existing.has(l)) {
      const opt = document.createElement("option");
      opt.value = l;
      opt.textContent = l;
      leagueSelect.appendChild(opt);
    }
  });

  // set default date to today
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const dd = String(today.getDate()).padStart(2, "0");
  startDateInput.value = `${yyyy}-${mm}-${dd}`;
}

// add filter to list
function addFilter() {
  const team = (teamInput.value || "").trim();
  const league = (leagueSelect.value || "Any");
  const start = startDateInput.value || null;
  const f = { team, league, start };
  // avoid exact duplicates
  if (FILTERS.some(x => x.team === f.team && x.league === f.league && x.start === f.start)) return;
  FILTERS.push(f);
  renderFilters();
}

// render filters list
function renderFilters() {
  filtersListEl.innerHTML = "";
  FILTERS.forEach((f, idx) => {
    const chip = document.createElement("div");
    chip.className = "filter-chip";
    const text = `${f.team || "Any team"} | ${f.league || "Any"} | ${f.start || "Any date"}`;
    chip.appendChild(document.createTextNode(text));
    const btn = document.createElement("button");
    btn.textContent = "✕";
    btn.title = "Remove filter";
    btn.onclick = () => { FILTERS.splice(idx, 1); renderFilters(); };
    chip.appendChild(btn);
    filtersListEl.appendChild(chip);
  });
}

// run filters: for each filter, find matches and union by link
function runFilters() {
  const unique = new Map(); // key: link or composite, value: item
  if (FILTERS.length === 0) {
    // if no filters, use default: startdate = today + league/team Any => return none or all?
    // we'll treat "no filters" as "use single filter: Any, Any, today"
    const defaultFilter = { team: "", league: "Any", start: startDateInput.value };
    FILTERS = [defaultFilter];
    renderFilters();
  }

  const minDurationHours = parseFloat(defaultDurationInput.value) || 2;

  for (const f of FILTERS) {
    const teamQ = (f.team || "").toLowerCase();
    const leagueQ = (f.league || "Any");
    const startQ = f.start ? new Date(f.start) : null;

    for (const item of DATA.matches) {
      // parse date
      if (!item.dateT) continue;
      const dt = new Date(item.dateT);
      if (isNaN(dt)) continue;

      // start date filter
      if (startQ && dt < startQ) continue;

      // league filter
      if (leagueQ && leagueQ !== "Any" && String(item.league || "").toLowerCase() !== String(leagueQ).toLowerCase()) continue;

      // team filter: match against title and location (case-insensitive substring)
      if (teamQ) {
        if (!(item.home.toLowerCase().includes(teamQ) || item.guest.toLowerCase().includes(teamQ)))
          continue;
      }

      // uniqueness key: prefer link if present
      const key = `${item.title}||${item.dateT}`;
      unique.set(key, item);
    }
  }

  // store results
  FILTERED = Array.from(unique.values()).sort((a, b) => new Date(a.dateT) - new Date(b.dateT));
  renderResults();
  renderCalendar();
}

// render results table
function renderResults() {
  resultsTableBody.innerHTML = "";
  resultsCount.textContent = `${FILTERED.length} result(s)`;
  FILTERED.forEach(it => {
    const tr = document.createElement("tr");
    const linkCell = `<a class="link" href="${it.link || '#'}" target="_blank" rel="noopener noreferrer">link</a>`;
    const dateStr = it.dateT ? new Date(it.dateT).toLocaleString() : "";
    tr.innerHTML = `<td>${escapeHtml(it.title || "")}</td>
                    <td>${escapeHtml(dateStr)}</td>
                    <td>${escapeHtml(it.location || "")}</td>
                    <td>${escapeHtml(it.league || "")}</td>
                    <td>${it.link ? `<a class="link" href="${it.link}" target="_blank">open</a>` : ""}</td>`;
    resultsTableBody.appendChild(tr);
  });
}

// escape helper
function escapeHtml(s) {
  return String(s || "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

/* === FullCalendar integration === */
let calendar;
function renderCalendar() {
  const calEl = document.getElementById("calendar");
  // prepare events
  const durationHours = parseFloat(defaultDurationInput.value) || 2;
  const events = FILTERED.map(it => {
    const start = it.dateT;
    const dt = new Date(start);
    const dtEnd = new Date(dt.getTime() + durationHours * 3600 * 1000);
    return {
      title: it.title,
      start: dt.toISOString(),
      end: dtEnd.toISOString(),
      url: it.link || undefined,
      extendedProps: { location: it.location || "", league: it.league || "" }
    };
  });

  if (!calendar) {
    calendar = new FullCalendar.Calendar(calEl, {
      initialView: 'dayGridMonth',
      locale: 'de',               // German locale (for months, days, etc.)
      firstDay: 1,                // Week starts on Monday
      slotLabelFormat: {          // 24-hour time format
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      },
      eventTimeFormat: {          // Also show events in 24h format
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      },
      eventContent: function (arg) {
        const wrapper = document.createElement('div');
        wrapper.style.display = 'flex';
        wrapper.style.flexDirection = 'column';
        wrapper.style.alignItems = 'flex-start';
        wrapper.style.lineHeight = '1.2em';

        const timeEl = document.createElement('div');
        timeEl.textContent = arg.timeText;
        timeEl.style.fontSize = '1em';

        const titleEl = document.createElement('div');
        titleEl.textContent = arg.event.title;
        titleEl.style.whiteSpace = 'normal';
        titleEl.style.fontSize = '0.85em';

        wrapper.appendChild(timeEl);
        wrapper.appendChild(titleEl);

        return { domNodes: [wrapper] };
      },
      headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,timeGridDay' },
      events,
    //   height: 500,
      eventClick: function (info) {
        // allow opening link in new tab if exists
        if (info.event.url) {
          window.open(info.event.url, "_blank");
          info.jsEvent.preventDefault();
        }
      }
    });
    calendar.render();
  } else {
    calendar.removeAllEvents();
    events.forEach(e => calendar.addEvent(e));
  }
}

/* === ICS generation === */
function toIcsDt(dateIso) {
  // returns YYYYMMDDTHHMMSS (local time)
  const d = new Date(dateIso);
  const pad = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}T${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function generateIcsContent(items) {
  const durHours = parseFloat(defaultDurationInput.value) || 2;
  const dtstamp = toIcsDt(new Date().toISOString());
  let ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ovv-scraper//EN\n";
  for (const it of items) {
    const dtstart = toIcsDt(it.dateT);
    const dtend = toIcsDt(new Date(new Date(it.dateT).getTime() + durHours * 3600 * 1000).toISOString());
    const uid = (it.title + it.dateT).replace(/\s+/g, "_").slice(0, 200);
    const summary = (it.title || "").replace(/[\r\n]+/g, " ");
    const desc = `Link: ${it.link || ''}`;
    const loc = it.location || "";
    ics += "BEGIN:VEVENT\n";
    ics += `UID:${uid}\n`;
    ics += `DTSTAMP:${dtstamp}\n`;
    ics += `DTSTART:${dtstart}\n`;
    ics += `DTEND:${dtend}\n`;
    ics += `SUMMARY:${escapeIcs(summary)}\n`;
    if (loc) ics += `LOCATION:${escapeIcs(loc)}\n`;
    if (desc) ics += `DESCRIPTION:${escapeIcs(desc)}\n`;
    ics += "END:VEVENT\n";
  }
  ics += "END:VCALENDAR\n";
  return ics;
}
function escapeIcs(s) { return String(s || "").replace(/\n/g, "\\n").replace(/,/g, "\\,"); }

/* === event wiring === */
addFilterBtn.addEventListener("click", e => { addFilter(); });
runFiltersBtn.addEventListener("click", e => { runFilters(); });
downloadIcsBtn.addEventListener("click", e => {
  if (!FILTERED.length) return alert("No filtered events to export.");
  const ics = generateIcsContent(FILTERED);
  download("matches.ics", ics, "text/calendar;charset=utf-8");
});

// boot
loadData().then(() => { /* nothing else */ });

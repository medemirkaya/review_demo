#!/usr/bin/env python3
"""Write epg.xml (XMLTV) into $OUT: yesterday through the next 7 days, relative to the run date.

Times carry an explicit UTC offset (timezone from channels.json). Programme lengths are
deterministic per channel and date, so re-running on the same day yields the same file.
Age marks use <rating system="VCHIP">.
Optional: NOW (ISO 8601 with offset) overrides the current time for testing.
"""
import json
import os
import random
from datetime import datetime, timedelta
from xml.sax.saxutils import escape, quoteattr
from zoneinfo import ZoneInfo

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.abspath(os.environ.get("OUT", os.path.join(ROOT, "out", "site")))
cfg = json.load(open(os.path.join(ROOT, "channels.json"), encoding="utf-8"))
tz = ZoneInfo(cfg["timezone"])
now = datetime.fromisoformat(os.environ["NOW"]) if os.environ.get("NOW") else datetime.now(tz)
today = now.astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)
start = today - timedelta(days=cfg["epg_days_back"])
end = today + timedelta(days=cfg["epg_days_forward"] + 1)

FILLER = [
    ("Test Pattern", "Synthetic sample programme used to fill the demo guide.", "Sample", "TV-G"),
    ("Sample Programme", "Placeholder entry for testing guide layout and now/next.", "Sample", "TV-G"),
    ("Guide Check", "Short placeholder entry for testing guide layout.", "Sample", "TV-G"),
]
LENGTHS = [30, 45, 60, 90, 120]


def stamp(dt):
    return dt.strftime("%Y%m%d%H%M%S ") + dt.strftime("%z")


def element(tag, text, **attrs):
    a = "".join(f" {k}={quoteattr(v)}" for k, v in attrs.items())
    return f"<{tag}{a}>{escape(text)}</{tag}>"


out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<tv generator-info-name="guidevi-review-demo">']
for ch in cfg["channels"]:
    out.append(f'  <channel id={quoteattr(ch["id"])}>')
    out.append("    " + element("display-name", ch["name"], lang="en"))
    out.append("  </channel>")

for ch in cfg["channels"]:
    film = cfg["films"][ch["film"]]
    cursor = start
    n = 0
    while cursor < end:
        day_rng = random.Random(f"{ch['id']}-{cursor.isoformat()}")
        if n % 3 == 0:
            title, desc, cat, rating = (f"{film['title']} ({film['year']})",
                                        f"{film['desc']} {film['credit']} ({film['license']}).",
                                        "Movie", film["rating"])
        else:
            title, desc, cat, rating = FILLER[(n // 3 + n) % len(FILLER)]
        length = day_rng.choice(LENGTHS)
        stop = min(cursor + timedelta(minutes=length), (cursor + timedelta(days=1)).replace(hour=0, minute=0, second=0))
        out.append(f'  <programme start="{stamp(cursor)}" stop="{stamp(stop)}" channel={quoteattr(ch["id"])}>')
        out.append("    " + element("title", title, lang="en"))
        out.append("    " + element("desc", desc, lang="en"))
        out.append("    " + element("category", cat, lang="en"))
        out.append(f'    <rating system="VCHIP"><value>{rating}</value></rating>')
        out.append("  </programme>")
        cursor = stop
        n += 1
out.append("</tv>")

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "epg.xml"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"epg.xml: {start.date()} .. {(end - timedelta(days=1)).date()} ({cfg['timezone']})")

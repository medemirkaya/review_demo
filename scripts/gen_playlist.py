#!/usr/bin/env python3
"""Write playlist.m3u into $OUT. Absolute URLs are built from $BASE_URL (hostname, no IP)."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.abspath(os.environ.get("OUT", os.path.join(ROOT, "out", "site")))
BASE = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")
cfg = json.load(open(os.path.join(ROOT, "channels.json"), encoding="utf-8"))

lines = [f'#EXTM3U url-tvg="{BASE}/epg.xml"',
         "# Guidevi review demo. Excerpts of Blender Foundation open movies (CC BY). See ATTRIBUTION.md."]
for ch in cfg["channels"]:
    film = cfg["films"][ch["film"]]
    lines.append(f"# {film['title']}: {film['credit']} ({film['license']})")
    lines.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-chno="{ch["number"]}" '
                 f'tvg-logo="{BASE}/{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}')
    lines.append(f"{BASE}/{ch['path']}")
for item in cfg.get("vod", []):
    film = cfg["films"][item["film"]]
    lines.append(f"# {film['title']}: {film['credit']} ({film['license']})")
    lines.append(f'#EXTINF:-1 tvg-name="{item["name"]}" group-title="{item["group"]}",{item["name"]}')
    lines.append(f"{BASE}/{item['path']}")

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "playlist.m3u"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"playlist.m3u: {len(cfg['channels'])} channels, {len(cfg.get('vod', []))} VOD")

# Guidevi review demo source

A sample source with openly licensed content, used to test the **Guidevi** app during App Store
review. It exists so a reviewer can add a working playlist and program guide without needing any
account or subscription. It is not a public TV service, and Guidevi itself contains no built-in
demo mode: the reviewer enters this source's URL like any other source.

All video is excerpted from Blender Foundation open movies (CC BY). See
[ATTRIBUTION.md](ATTRIBUTION.md) for licenses and credit lines.

## URLs

After publishing (see Setup), with `<user>` and `<repo>` replaced:

| What | URL |
|---|---|
| Playlist (M3U) | `https://<user>.github.io/<repo>/playlist.m3u` |
| Program guide (XMLTV) | `https://<user>.github.io/<repo>/epg.xml` |
| Landing page | `https://<user>.github.io/<repo>/` |

The playlist's `url-tvg` header already points to the guide, so adding only the playlist is enough.
Everything is served over HTTPS from a hostname (no IP addresses).

## What is published

| Channel | `tvg-id` | Group | Stream |
|---|---|---|---|
| Meadow TV | `meadow.demo` | Kısa | HLS (MPEG-TS segments, H.264/AAC) |
| Dragon Cinema | `dragon.demo` | Filmler | HLS |
| Steel Screen | `steel.demo` | Filmler | raw MPEG-TS file (`.ts`) |
| Dream Reel | `dream.demo` | Kısa | HLS |

Plus two MP4 entries in the group "Film Arşivi" (VOD-style, direct file URLs).

- Each channel plays a 90 second excerpt. The streams are on-demand files, not live: they end
  after the excerpt. Program times in the guide are relative to the current date and are
  deliberately not synchronized with the excerpt.
- `epg.xml` covers yesterday through the next 7 days, with an explicit UTC offset on every time
  (zone set in `channels.json`, default `Europe/Istanbul`), contiguous programmes for every
  channel, and age marks as `<rating system="VCHIP">` (TV-G / TV-PG).
- Channel IDs in the guide match the playlist's `tvg-id` values.

## Setup

1. Create a new **public** GitHub repository (for example `guidevi-review-demo`) and push the
   contents of this folder to its `main` branch (the folder's contents become the repo root; keep
   `.github/`).
2. In the repository, open **Settings > Pages** and set **Source** to **GitHub Actions**.
3. Open the **Actions** tab, choose "Publish demo source" and press **Run workflow** (a push to
   `main` also triggers it). The first run downloads the sources and takes a few minutes.
4. When the run is green, the URLs above work. Check them with
   `curl -I https://<user>.github.io/<repo>/playlist.m3u` and open the `.m3u8` in Safari.
5. The workflow also runs every day at 02:17 UTC to regenerate `epg.xml`. GitHub pauses scheduled
   workflows in repositories with no activity for 60 days; if the guide goes stale, open the
   Actions tab and re-enable it (or run it manually). Do this shortly before submitting to
   review.

Optional: set a custom domain in Pages settings; the workflow reads the base URL from GitHub, so
playlist URLs follow automatically.

## Local build (for testing)

Requires Python 3.9+, ffmpeg with libx264 and aac.

```sh
export BASE_URL=http://localhost:8000
export CLIP_SECONDS=10           # default 90
python3 scripts/build_media.py   # downloads/streams the sources, writes out/site
python3 scripts/gen_playlist.py
python3 scripts/gen_epg.py
cd out/site && python3 -m http.server 8000
```

`out/` is git-ignored. Limits respected by the default settings: whole site is about 50 MB
(Pages limit: 1 GB), largest file about 11 MB (GitHub file limit: 100 MB). The build script fails
if a file exceeds 90 MB or the site exceeds 900 MB.

`scripts/make_logos.py` redraws the monogram logos in `static/logos` (already committed).

## Layout

| Path | Purpose |
|---|---|
| `channels.json` | channel list, film credits, source URLs and start offsets |
| `scripts/build_media.py` | ffmpeg: one H.264/AAC encode per film, then HLS, `.ts`, MP4 |
| `scripts/gen_playlist.py` | writes `playlist.m3u` |
| `scripts/gen_epg.py` | writes `epg.xml` (run date relative) |
| `static/` | landing page and logos, copied into the site |
| `.github/workflows/pages.yml` | build and deploy to GitHub Pages, daily |

## Later

An optional Xtream-style demo (a small Cloudflare Worker returning canned JSON for review only)
is planned but not part of this repository yet.

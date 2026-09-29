#!/usr/bin/env python3
"""Build the demo media: short HLS (MPEG-TS segments, H.264/AAC), one raw .ts, two MP4 VOD files.

Sources are the official Blender Foundation open-movie downloads (CC BY, see ATTRIBUTION.md).
Nothing is committed; output goes to $OUT (default: out/site).

Environment:
  OUT           output directory (default out/site)
  CACHE         download cache (default out/cache)
  CLIP_SECONDS  clip length per film (default 90). Delete $CACHE/encoded after changing it.
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.abspath(os.environ.get("OUT", os.path.join(ROOT, "out", "site")))
CACHE = os.path.abspath(os.environ.get("CACHE", os.path.join(ROOT, "out", "cache")))
CLIP = int(os.environ.get("CLIP_SECONDS", "90"))
cfg = json.load(open(os.path.join(ROOT, "channels.json"), encoding="utf-8"))


def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def source_input(key):
    """Returns an ffmpeg input (URL or local path). Zipped sources are downloaded and extracted once."""
    src = cfg["sources"][key]
    if not src["zip"]:
        return src["url"]  # ffmpeg seeks over HTTP range requests; only the needed bytes are read
    os.makedirs(CACHE, exist_ok=True)
    target = os.path.join(CACHE, f"{key}.src")
    if not os.path.exists(target):
        archive = os.path.join(CACHE, f"{key}.zip")
        print(f"downloading {src['url']}", flush=True)
        request = urllib.request.Request(src["url"], headers={"User-Agent": "guidevi-review-demo/1.0"})
        with urllib.request.urlopen(request, timeout=120) as resp, open(archive, "wb") as fout:
            shutil.copyfileobj(resp, fout)
        with zipfile.ZipFile(archive) as z:
            member = max(z.infolist(), key=lambda i: i.file_size)
            with z.open(member) as fin, open(target, "wb") as fout:
                shutil.copyfileobj(fin, fout)
        os.remove(archive)
    return target


def encode(key, dest):
    """One H.264/AAC encode per film (2 s GOP so every remux cuts cleanly on keyframes)."""
    run(["-ss", str(cfg["sources"][key]["start"]), "-t", str(CLIP), "-i", source_input(key),
         "-map", "0:v:0", "-map", "0:a:0?", "-dn", "-sn", "-map_chapters", "-1", "-map_metadata", "-1",
         "-vf", "scale=w='if(gt(ih,480),-2,trunc(iw/2)*2)':h='if(gt(ih,480),480,trunc(ih/2)*2)',fps=24,format=yuv420p",
         "-c:v", "libx264", "-profile:v", "main", "-preset", "veryfast", "-crf", "24",
         "-g", "48", "-keyint_min", "48", "-sc_threshold", "0",
         "-c:a", "aac", "-b:a", "96k", "-ac", "2", "-ar", "48000",
         "-movflags", "+faststart", dest])


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    work = os.path.join(CACHE, "encoded")
    os.makedirs(work, exist_ok=True)
    encoded = {}
    for key in cfg["films"]:
        encoded[key] = os.path.join(work, f"{key}.mp4")
        if not os.path.exists(encoded[key]):  # kept in the CI cache between daily runs
            encode(key, encoded[key])

    for ch in cfg["channels"]:
        src = encoded[ch["film"]]
        dest = os.path.join(OUT, ch["path"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if ch["kind"] == "hls":
            run(["-i", src, "-c", "copy", "-f", "hls", "-hls_time", "6",
                 "-hls_playlist_type", "vod", "-hls_segment_type", "mpegts",
                 "-hls_segment_filename", os.path.join(os.path.dirname(dest), "seg_%03d.ts"), dest])
        else:
            run(["-i", src, "-c", "copy", "-f", "mpegts", dest])

    for item in cfg.get("vod", []):
        dest = os.path.join(OUT, item["path"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(encoded[item["film"]], dest)

    for name in os.listdir(os.path.join(ROOT, "static")):
        src = os.path.join(ROOT, "static", name)
        shutil.copytree(src, os.path.join(OUT, name)) if os.path.isdir(src) else shutil.copy(src, OUT)

    total = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    biggest = max(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
    print(f"media done: {total / 1e6:.1f} MB total, largest file {biggest / 1e6:.1f} MB")
    if total > 900e6 or biggest > 90e6:
        sys.exit("output exceeds Pages limits (site <= 1 GB, file < 100 MB); lower CLIP_SECONDS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Draw the monogram logos in static/logos (original artwork, no real channel marks)."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

LOGOS = {"meadow": ("M", (46, 125, 90)), "dragon": ("D", (150, 52, 60)),
         "steel": ("S", (60, 76, 110)), "dream": ("R", (120, 80, 150))}
FONTS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
out = os.path.join(os.path.dirname(__file__), "..", "static", "logos")
os.makedirs(out, exist_ok=True)
font_path = next((p for p in FONTS if os.path.exists(p)), None)
if font_path is None:
    sys.exit("no bold font found")
font = ImageFont.truetype(font_path, 150)
for name, (letter, color) in LOGOS.items():
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((8, 8, 248, 248), radius=56, fill=color + (255,))
    d.text((128, 132), letter, font=font, fill=(255, 255, 255, 255), anchor="mm")
    img.save(os.path.join(out, f"{name}.png"), optimize=True)

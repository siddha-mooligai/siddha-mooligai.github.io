"""Make one passport-size (35x45 mm, 600 dpi) QR sticker PNG per plant.

Run:  python tools/make_stickers.py
Output: qr-stickers/NN_<id>.png   (needs Microsoft Edge + Pillow: pip install pillow)
"""
import json, subprocess, sys, tempfile, urllib.parse
from pathlib import Path
from PIL import Image

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = "https://siddha-mooligai.github.io/plants/"
here = Path(__file__).parent
project = here.parent
out_dir = project / "qr-stickers"
out_dir.mkdir(parents=True, exist_ok=True)
template = (here / "sticker.html").resolve().as_uri()
plants = json.loads((project / "plants.json").read_text(encoding="utf-8"))

for n, p in enumerate(plants, 1):
    url = BASE + p["id"] + "/"
    page = template + "?" + urllib.parse.urlencode({"ta": p["tamil_name"], "url": url})
    out = out_dir / f"{n:02d}_{p['id']}.png"
    subprocess.run([EDGE, "--headless=new", f"--user-data-dir={tempfile.gettempdir()}/siddha-edge-profile", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=413,531", "--force-device-scale-factor=2",
                    "--virtual-time-budget=8000", f"--screenshot={out}", page],
                   check=True, capture_output=True)
    img = Image.open(out).convert("RGB")
    img.save(out, dpi=(600, 600))  # 826x1062 px @600dpi = 35x45 mm
    print(f"{out.name}: {img.size} -> {url}")

"""Generate the plant pages from plants.json.

Run:  python build.py
Creates:  index.html  and  plants/<id>/index.html  for every plant.
Uses only the Python standard library.
"""
import hashlib
import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
PLANTS_DIR = ROOT / "plants"

SITE_TITLE = "சித்த மூலிகைக் கண்காட்சி"
CENTRE_NAME = "முத்துப்பேட்டை சித்த ஆரம்ப சுகாதார மையம்"
# Links shown on the home page, as (label, relative URL). Add more here.
HOME_LINKS = [  # (icon, label, link) — shown as tiles on the home page, after the visiting-hours tile
    ("🌿", "சித்த மூலிகைக் கண்காட்சி", "plants/"),
    ("🩺", "சித்த மருத்துவ முகாம்", "camp/"),
    ("🏥", "சிகிச்சைப் பிரிவு", "clinic/"),
    ("🧹", "தூய்மைப் பணிகள்", "cleanliness/"),
    ("🏛️", "மையத்தின் வெளிப்புறத் தோற்றம்", "outerview/"),
    ("🪴", "சித்த மூலிகைத் தோட்டம்", "garden/"),
    ("🏫", "SHP", "shp/"),
    ("🤰", "மகப்பேறு சஞ்சீவி (MSK)", "msk/"),
    ("💬", "பயனாளிகளின் அனுபவங்கள் (Testimonials)", "testimonials/"),
]
# Photo galleries: (folder id, page title). Put original photos in photos/<id>/ (kept local, not
# uploaded); the build writes resized web copies to <id>/img and <id>/thumb. Optional captions:
# photos/<id>/captions.json  ->  {"photo1.jpg": "caption text", ...}
GALLERIES = [
    ("camp", "சித்த மருத்துவ முகாம்"),
    ("clinic", "சிகிச்சைப் பிரிவு"),
    ("cleanliness", "தூய்மைப் பணிகள்"),
    ("outerview", "மையத்தின் வெளிப்புறத் தோற்றம்"),
    ("garden", "சித்த மூலிகைத் தோட்டம்"),
    ("shp", "SHP"),
    ("msk", "மகப்பேறு சஞ்சீவி (MSK)"),
    ("testimonials/diabetic-foot", "சர்க்கரை நோய் பாதப் புண் (Diabetic Foot)"),
    ("testimonials/diabetic-hba1c", "சர்க்கரை நோய் – HbA1c (Diabetic HbA1c)"),
]
# Visiting hours — shown as the first home-page tile (live open/closed status, India time).
# Open Monday–Saturday from OPEN_FROM to OPEN_UNTIL (24-hour "HH:MM"); closed on Sundays
# and on the dates in GOVT_HOLIDAYS ("YYYY-MM-DD"). Logic lives in hours.js.
OPEN_FROM, OPEN_UNTIL = "09:00", "16:00"
GOVT_HOLIDAYS = [
    # "2026-12-25",
]
GOATCOUNTER ="siddha-mooligai"  # https://siddha-mooligai.goatcounter.com (view & like counts)
DISCLAIMER ="இத்தகவல்கள் விழிப்புணர்வுக்காக மட்டுமே. எந்த மூலிகையையும் பயன்படுத்தும் முன் தகுதியான சித்த மருத்துவரை அணுகவும்."

HEAD = """<!doctype html>
<html lang="ta">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&display=swap">
<link rel="stylesheet" href="{css}?v={css_version}">
<script>window.goatcounter = {{path: function (p) {{ return p.replace(/[/]+(?=$|[?])/, '') || '/'; }}}};</script>
<script data-goatcounter="https://{goatcounter}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</head>
<body>
"""

FOOT = """<footer>{disclaimer}</footer>
</body>
</html>
"""


def asset_version(name):
    """Short content hash, appended as ?v=... so phones fetch the new file after every change."""
    return hashlib.md5((ROOT / name).read_bytes()).hexdigest()[:8]


def li_list(items):
    return "\n".join(f"<li>{escape(i)}</li>" for i in items)


def section(heading, body):
    return f'<section><h2>{heading}</h2>{body}</section>' if body else ""


def has_content(p):
    return any(p.get(k) for k in ("facts", "note", "description", "parts_used", "uses", "how_to_use", "caution"))


def facts_block(p):
    if not p.get("facts"):
        return ""
    out = []
    if p.get("facts_heading"):
        out.append(f'<h2 class="facts-heading">{escape(p["facts_heading"])}</h2>')
    for n, f in enumerate(p["facts"], 1):
        out.append(f'<section class="fact"><h3><span class="num">{n}</span>{escape(f["title"])}</h3>'
                   f'<p>{escape(f["text"])}</p></section>')
    return "\n".join(out)


def note_block(p):
    if not p.get("note"):
        return ""
    heading = escape(p.get("note_heading", ""))
    cls = "note warning" if p.get("note_heading", "").startswith("⚠") else "note"
    warn = f'<p class="note-warn">{escape(p["note_warning"])}</p>' if p.get("note_warning") else ""
    key = (f'<p class="note-key"><b>{escape(p.get("key_benefit_label", "🎯 முக்கியப் பயன்:"))}</b> '
           f'{escape(p["key_benefit"])}</p>') if p.get("key_benefit") else ""
    return (f'<section class="{cls}">{f"<h2>{heading}</h2>" if heading else ""}'
            f'<p>{escape(p["note"])}</p>{key}{warn}</section>')


def plant_page(p):
    e = {k: escape(v) if isinstance(v, str) else v for k, v in p.items()}
    img = ""
    if p.get("image") and (ROOT / p["image"]).exists():
        credit = ""
        c = p.get("image_credit")
        if c:
            credit = (f'<figcaption>படம்: {escape(c["author"])} · {escape(c["license"])} · '
                      f'<a href="{escape(c["source"])}" target="_blank" rel="noopener">Wikimedia Commons</a></figcaption>')
        img = (f'<figure class="photo"><img src="../../{e["image"]}" alt="{e["tamil_name"]}" '
               f'width="100%" loading="eager">{credit}</figure>')

    body = f"""<header class="hero">
  <h1>{e['tamil_name']}</h1>
  <p class="sub">{e['english_name']}{f" · <i>{e['botanical_name']}</i>" if p.get("botanical_name") else ""}</p>
</header>
<main>
{img}
{note_block(p)}
{facts_block(p)}
{section("வேறு பெயர்கள்", f"<p>{e.get('other_names', '')}</p>" if p.get('other_names') else "")}
{section("அறிமுகம்", f"<p>{e['description']}</p>" if p.get("description") else "")}
{"" if has_content(p) else '<section><p>இந்த மூலிகை பற்றிய தகவல்கள் விரைவில் சேர்க்கப்படும்.</p></section>'}
{section("பயன்படும் பாகங்கள்", f'<ul class="chips">{li_list(p.get("parts_used", []))}</ul>' if p.get("parts_used") else "")}
{section("மருத்துவப் பயன்கள்", f"<ul>{li_list(p.get('uses', []))}</ul>" if p.get("uses") else "")}
{section("பயன்படுத்தும் முறை", f"<p>{e['how_to_use']}</p>" if p.get("how_to_use") else "")}
{f'<section class="caution"><h2>⚠ எச்சரிக்கை</h2><p>{e["caution"]}</p></section>' if p.get("caution") else ""}
<section class="like" id="like" data-id="{e['id']}">
  <p>இந்தத் தகவல் பயனுள்ளதாக இருந்ததா?</p>
  <div class="like-row">
    <div class="like-left">
      <button type="button">👍 ஆம்</button>
      <span class="like-count" aria-live="polite"></span>
    </div>
    <span class="views" id="views" hidden>👁 <span></span> பார்வைகள்</span>
  </div>
</section>
<nav class="bottombar">
  <a class="back" href="../">← அனைத்து மூலிகைகள்</a>
  <a class="home" href="../../">🏠 முகப்பு</a>
</nav>
</main>
<script src="../../stats.js?v={asset_version('stats.js')}" defer></script>
"""
    return (HEAD.format(title=f"{e['tamil_name']} – {SITE_TITLE}", css="../../style.css", css_version=asset_version("style.css"), goatcounter=GOATCOUNTER)
            + body + FOOT.format(disclaimer=DISCLAIMER))


def tile_cover(href, plant_count):
    """(cover image URL or None, count text) for a home tile."""
    def thumbs_of(gid):
        d = ROOT / gid / "thumb"
        return sorted(d.glob("*.jpg")) if d.exists() else []
    if href == "plants/":
        cover = ROOT / "images" / "cover-plants.jpg"
        if not cover.exists() or cover.stat().st_mtime < (ROOT / PLANTS_COVER).stat().st_mtime:
            from PIL import Image
            im = Image.open(ROOT / PLANTS_COVER).convert("RGB"); im.thumbnail((500, 500))
            im.save(cover, "JPEG", quality=75, optimize=True, progressive=True)
        return f"images/cover-plants.jpg?v={asset_version('images/cover-plants.jpg')}", f"{plant_count} மூலிகைகள்"
    gid = href.rstrip("/")
    section = next((cards for folder, _, cards in SECTIONS if folder == gid), None)
    groups = [f"{gid}/{h.rstrip('/')}" for _, _, h in section] if section else [gid]
    thumbs = [t for g in groups for t in thumbs_of(g)]
    if not thumbs:
        return None, ""
    pick = COVERS.get(href)
    first = next((t for t in thumbs if t.name == pick), thumbs[0])
    # Cover = the original photo WITHOUT the title band (a cropped band looks untidy on a tile).
    # Made from the local original in photos/<gallery>/; falls back to the titled thumbnail.
    gallery = first.parent.parent.relative_to(ROOT).as_posix()
    original = next((o for o in (ROOT / "photos" / gallery).glob(first.stem + ".*")
                     if o.suffix.lower() in PHOTO_EXTS), None)
    cover = ROOT / "images" / "covers" / (gid.replace("/", "-") + ".jpg")
    if original:
        if not cover.exists() or cover.stat().st_mtime < original.stat().st_mtime or COVERS.get(href):
            from PIL import Image, ImageOps
            cover.parent.mkdir(parents=True, exist_ok=True)
            im = ImageOps.exif_transpose(Image.open(original)).convert("RGB"); im.thumbnail((500, 500))
            im.save(cover, "JPEG", quality=75, optimize=True, progressive=True)
    rel = (cover if cover.exists() else first).relative_to(ROOT).as_posix()
    return f"{rel}?v={asset_version(rel)}", f"{len(thumbs)} படங்கள்"


def plant_slides(plants):
    """Small (500px) copies of every plant photo for the home-page slideshow: [{src, name}]."""
    from PIL import Image
    out_dir = ROOT / "images" / "slides"; out_dir.mkdir(parents=True, exist_ok=True)
    slides = []
    for p in plants:
        src = ROOT / p.get("image", "")
        if not p.get("image") or not src.exists():
            continue
        dst = out_dir / f"{p['id']}.jpg"
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            im = Image.open(src).convert("RGB"); im.thumbnail((500, 500))
            im.save(dst, "JPEG", quality=72, optimize=True, progressive=True)
        rel = dst.relative_to(ROOT).as_posix()
        slides.append({"src": f"{rel}?v={asset_version(rel)}", "name": p["tamil_name"]})
    return slides


def home_page(plants):
    """Landing page: logo, centre name, a live visiting-hours tile, then the activity tiles (HOME_LINKS)."""
    plant_count = len(plants)
    parts = []
    for icon, label, href in HOME_LINKS:
        cover, count = tile_cover(href, plant_count)
        if cover and href == "plants/":
            # Plant exhibition tile: slow cross-fade slideshow through all plant photos (slideshow.js)
            slides = plant_slides(plants)
            first = slides[0] if slides else {"src": cover, "name": ""}
            parts.append(
                f'<li><a class="tile has-cover" href="{escape(href)}">'
                f'<span class="tile-cover slideshow" id="plant-slides">'
                f'<img class="slide on" src="{escape(first["src"])}" alt="">'
                f'<img class="slide" alt="">'
                f'<span class="slide-name" id="slide-name">{escape(first["name"])}</span></span>'
                f'<script type="application/json" id="slides-data">{json.dumps(slides, ensure_ascii=False)}</script>'
                f'<span class="tile-body"><span class="tile-label"><span aria-hidden="true">{icon}</span> {escape(label)}</span>'
                f'<span class="tile-count">{escape(count)}</span></span></a></li>')
        elif cover:
            parts.append(
                f'<li><a class="tile has-cover" href="{escape(href)}">'
                f'<span class="tile-cover"><img src="{escape(cover)}" alt="" loading="lazy"></span>'
                f'<span class="tile-body"><span class="tile-label"><span aria-hidden="true">{icon}</span> {escape(label)}</span>'
                f'<span class="tile-count">{escape(count)}</span></span></a></li>')
        else:
            parts.append(
                f'<li><a class="tile" href="{escape(href)}"><span class="tile-icon" aria-hidden="true">{icon}</span>'
                f'<span class="tile-label">{escape(label)}</span></a></li>')
    tiles = "\n".join(parts)
    config = json.dumps({"from": OPEN_FROM, "until": OPEN_UNTIL, "holidays": GOVT_HOLIDAYS})
    body = f"""<header class="hero home-hero">
  <div class="logo"><img src="images/logo.png" alt="தமிழ்நாடு அரசு சின்னம்" width="80" height="87"></div>
  <h1>{CENTRE_NAME}</h1>
</header>
<main>
<ul class="home-tiles">
<li><button class="tile status-tile" id="st-tile" type="button" aria-haspopup="dialog">
  <span class="tile-icon" id="st-icon" aria-hidden="true">🕘</span>
  <span class="tile-label" id="st-label">வருகை நேரம்</span>
  <span class="st-clock" id="st-clock">திங்கள் – சனி</span>
  <span class="st-next" id="st-next">காலை 9:00 – மாலை 4:00</span>
</button></li>
{tiles}
</ul>
</main>
<div class="hours-overlay" id="hours-overlay" hidden>
  <div class="hours-panel" role="dialog" aria-modal="true" aria-labelledby="hours-title">
    <div class="hours-panel-head"><h2 id="hours-title">🕘 வருகை நேரம்</h2>
      <button type="button" class="hours-close" id="hours-close" aria-label="மூடு">✕</button></div>
    <div id="hours-table"></div>
    <p class="hours-note">அரசு விடுமுறை நாட்களிலும் விடுமுறை.</p>
  </div>
</div>
<script type="application/json" id="hours-config">{config}</script>
<script src="hours.js?v={asset_version('hours.js')}" defer></script>
<script src="slideshow.js?v={asset_version('slideshow.js')}" defer></script>
"""
    return HEAD.format(title=CENTRE_NAME, css="style.css", css_version=asset_version("style.css"), goatcounter=GOATCOUNTER) + body + FOOT.format(disclaimer="")


# Home tiles show a cover photo (first photo of the category) and a photo count. To choose a
# different cover: COVERS = {"clinic/": "clinic-06.jpg"}. The plant tile uses PLANTS_COVER.
COVERS = {}
PLANTS_COVER = "images/sangupoo.jpg"

# Section pages: a page of cards that open sub-galleries. (folder, title, [(icon, label, link)])
SECTIONS = [
    ("testimonials", "பயனாளிகளின் அனுபவங்கள் (Testimonials)", [
        ("🦶", "சர்க்கரை நோய் பாதப் புண் (Diabetic Foot)", "diabetic-foot/"),
        ("🧪", "சர்க்கரை நோய் – HbA1c (Diabetic HbA1c)", "diabetic-hba1c/"),
    ]),
]

PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
# Title band added above every gallery photo (the photo itself is not covered). Set to [] to turn off.
PHOTO_TITLE = ["GPHC - Muthupettai", "Thiruvarur - Dt"]
TITLE_FONT = r"C:\Windows\Fonts\segoeuib.ttf"


def add_title_band(im):
    """Return a new image: a green band with PHOTO_TITLE lines, then the full photo underneath."""
    if not PHOTO_TITLE:
        return im
    from PIL import Image, ImageDraw, ImageFont
    w, h = im.size
    unit = max(30, round(min(w, h) * 0.05))                 # scales with the photo
    sizes = [round(unit * 1.0), round(unit * 0.72)]          # first line bigger, second smaller
    def font(sz):
        try:
            return ImageFont.truetype(TITLE_FONT, sz)
        except OSError:
            return ImageFont.load_default()
    probe = ImageDraw.Draw(im)
    for i, line in enumerate(PHOTO_TITLE):                   # shrink to fit narrow photos
        while sizes[min(i, 1)] > 12 and probe.textlength(line, font=font(sizes[min(i, 1)])) > w * 0.9:
            sizes[min(i, 1)] -= 2
    gap, pad = round(unit * 0.2), round(unit * 0.35)
    heights = [sizes[min(i, 1)] for i in range(len(PHOTO_TITLE))]
    band = pad * 2 + sum(heights) + gap * (len(PHOTO_TITLE) - 1)
    out = Image.new("RGB", (w, h + band), (46, 107, 47))
    out.paste(im, (0, band))
    d = ImageDraw.Draw(out); y = pad
    for i, line in enumerate(PHOTO_TITLE):
        sz = heights[i]
        d.text((w / 2, y + sz / 2), line, font=font(sz), fill="white", anchor="mm")
        y += sz + gap
    return out


def build_gallery(gid, title):
    """Resize photos/<gid>/* into <gid>/img (1600px) and <gid>/thumb (500px); write <gid>/index.html."""
    src, out = ROOT / "photos" / gid, ROOT / gid
    up = "../" * (gid.count("/") + 1)  # path back to the site root
    src.mkdir(parents=True, exist_ok=True)
    originals = sorted(f for f in src.iterdir() if f.suffix.lower() in PHOTO_EXTS)
    captions = {}
    if (src / "captions.json").exists():
        captions = json.loads((src / "captions.json").read_text(encoding="utf-8"))
    names = []
    if originals:
        from PIL import Image, ImageOps  # only needed when there are photos
        for sub in ("img", "thumb"):
            (out / sub).mkdir(parents=True, exist_ok=True)
        for f in originals:
            name = f.stem + ".jpg"
            names.append((name, captions.get(f.name, "")))
            targets = [(out / "img" / name, 1600, 82), (out / "thumb" / name, 500, 75)]
            if all(t.exists() and t.stat().st_mtime >= f.stat().st_mtime for t, _, _ in targets):
                continue
            im = add_title_band(ImageOps.exif_transpose(Image.open(f)).convert("RGB"))
            for t, size, q in targets:
                c = im.copy(); c.thumbnail((size, size))
                c.save(t, "JPEG", quality=q, optimize=True, progressive=True)  # re-save drops EXIF/GPS
    keep = {n for n, _ in names}
    for sub in ("img", "thumb"):  # remove web copies whose original was deleted
        if (out / sub).exists():
            for t in (out / sub).iterdir():
                if t.name not in keep:
                    t.unlink()
    out.mkdir(exist_ok=True)
    def ver(p):  # content hash, so browsers fetch a photo again whenever it changes
        return hashlib.md5(p.read_bytes()).hexdigest()[:8]
    if names:
        items = "\n".join(
            f'<li><button type="button" class="g-item" data-full="img/{escape(n)}?v={ver(out / "img" / n)}" data-cap="{escape(c)}">'
            f'<img src="thumb/{escape(n)}?v={ver(out / "thumb" / n)}" alt="{escape(c or title)}" loading="lazy"></button>'
            f'{f"<p>{escape(c)}</p>" if c else ""}</li>'
            for n, c in names)
        content = f'<ul class="gallery g-{gid.replace("/", "-")}">\n{items}\n</ul>'
    else:
        content = '<section><p>புகைப்படங்கள் விரைவில் சேர்க்கப்படும்.</p></section>'
    location = ""
    if gid == "outerview":
        maps_url = "https://maps.google.com/maps?cid=8280755249423740902"
        location = f"""<section aria-labelledby="location-heading">
  <h2 id="location-heading">மையத்தின் இருப்பிடம்</h2>
  <p><a href="{maps_url}" style="display:inline-flex;align-items:center;min-height:44px">Google Maps-ல் திறக்கவும்</a></p>
  <iframe title="முத்துப்பேட்டை சித்த ஆரம்ப சுகாதார மையத்தின் வரைபடம்"
    src="{maps_url}&amp;output=embed" loading="lazy" height="320"
    style="display:block;width:100%;border:0" allowfullscreen></iframe>
</section>"""
    body = f"""<header class="hero">
  <h1>{escape(title)}</h1>
  <p class="sub">{CENTRE_NAME}</p>
</header>
<main>
<div class="list-top">
  <h2 class="list-heading">புகைப்படங்கள் ({len(names)})</h2>
  <a class="home" href="{up}">🏠 முகப்பு</a>
</div>
{content}
{location}
{'<nav class="bottombar"><a class="back" href="../">← திரும்பிச் செல்ல</a><span></span></nav>' if "/" in gid else ""}
</main>
<div class="lightbox" id="lightbox" hidden>
  <button type="button" class="lb-close" id="lb-close" aria-label="மூடு">✕</button>
  <button type="button" class="lb-nav lb-prev" id="lb-prev" aria-label="முந்தைய">‹</button>
  <figure><img id="lb-img" alt=""><figcaption id="lb-cap"></figcaption></figure>
  <button type="button" class="lb-nav lb-next" id="lb-next" aria-label="அடுத்த">›</button>
</div>
<script src="{up}gallery.js?v={asset_version('gallery.js')}" defer></script>
"""
    (out / "index.html").write_text(
        HEAD.format(title=title, css=up + "style.css", css_version=asset_version("style.css"), goatcounter=GOATCOUNTER)
        + body + FOOT.format(disclaimer=""), encoding="utf-8")
    return len(names)


def section_page(folder, title, cards):
    """A page of cards (like the home tiles) linking to sub-galleries, e.g. /testimonials/."""
    tiles = "\n".join(
        f'<li><a class="tile" href="{escape(href)}"><span class="tile-icon" aria-hidden="true">{icon}</span>'
        f'<span class="tile-label">{escape(label)}</span></a></li>'
        for icon, label, href in cards)
    body = f"""<header class="hero">
  <h1>{escape(title)}</h1>
  <p class="sub">{CENTRE_NAME}</p>
</header>
<main>
<div class="list-top"><span></span><a class="home" href="../">🏠 முகப்பு</a></div>
<ul class="home-tiles">
{tiles}
</ul>
</main>
"""
    (ROOT / folder).mkdir(exist_ok=True)
    (ROOT / folder / "index.html").write_text(
        HEAD.format(title=title, css="../style.css", css_version=asset_version("style.css"), goatcounter=GOATCOUNTER)
        + body + FOOT.format(disclaimer=""), encoding="utf-8")


def list_page(plants):
    """Plant list at /plants/."""
    cards = "\n".join(
        f'<li><a href="{escape(p["id"])}/"><span class="names"><strong>{escape(p["tamil_name"])}</strong>'
        f'<span>{escape(p["english_name"])}</span></span><span class="chev" aria-hidden="true">›</span></a></li>'
        for p in plants
    )
    body = f"""<header class="hero">
  <h1>{SITE_TITLE}</h1>
  <p class="sub">ஒவ்வொரு மூலிகையின் அருகில் உள்ள QR குறியீட்டை ஸ்கேன் செய்யவும்</p>
</header>
<main>
<div class="list-top">
  <h2 class="list-heading">மூலிகைகள் ({len(plants)})</h2>
  <a class="home" href="../">🏠 முகப்பு</a>
</div>
<ul class="plant-list">
{cards}
</ul>
</main>
"""
    return HEAD.format(title=SITE_TITLE, css="../style.css", css_version=asset_version("style.css"), goatcounter=GOATCOUNTER) + body + FOOT.format(disclaimer=DISCLAIMER)


def main():
    plants = json.loads((ROOT / "plants.json").read_text(encoding="utf-8"))
    ids = [p["id"] for p in plants]
    if len(ids) != len(set(ids)):
        raise SystemExit("Error: duplicate plant id in plants.json")

    if PLANTS_DIR.exists():
        shutil.rmtree(PLANTS_DIR)
    for p in plants:
        out = PLANTS_DIR / p["id"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(plant_page(p), encoding="utf-8")
        if p.get("image") and not (ROOT / p["image"]).exists():
            print(f"  note: image not found for {p['id']}: {p['image']}")

    (PLANTS_DIR / "index.html").write_text(list_page(plants), encoding="utf-8")
    for folder, title, cards in SECTIONS:
        section_page(folder, title, cards)
    for gid, title in GALLERIES:
        print(f"Gallery {gid}: {build_gallery(gid, title)} photos")
    (ROOT / "index.html").write_text(home_page(plants), encoding="utf-8")  # after galleries: uses their thumbnails
    print(f"Built {len(plants)} plant pages.")


if __name__ == "__main__":
    main()

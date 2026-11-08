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
HOME_LINKS = [  # (icon, label, link) — shown as tiles on the home page
    ("🌿", "சித்த மூலிகைக் கண்காட்சி", "plants/"),
    ("🩺", "சித்த மருத்துவ முகாம்", "camp/"),
]
# Visiting hours box at the bottom of the home page: (days, time) rows
VISIT_HOURS_TITLE = "🕘 வருகை நேரம்"
VISIT_HOURS = [
    ("திங்கள் – சனி", "காலை 9:00 – மாலை 4:00"),
    ("ஞாயிறு & அரசு விடுமுறை நாட்கள்", "விடுமுறை"),
]
# Live open/closed status (India time): open Mon–Sat from OPEN_FROM to OPEN_UNTIL (24-hour "HH:MM"),
# closed on Sundays and on the dates in GOVT_HOLIDAYS ("YYYY-MM-DD").
OPEN_FROM, OPEN_UNTIL = "09:00", "16:00"
GOVT_HOLIDAYS = [
    # "2026-12-25",
]
CAMP_TITLE = "சித்த மருத்துவ முகாம்"
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


def home_page():
    """Landing page: logo, centre name and a few big links (more links can be added to HOME_LINKS)."""
    tiles = "\n".join(
        f'<li><a href="{escape(href)}"><span class="tile-icon" aria-hidden="true">{icon}</span>'
        f'<span class="tile-label">{escape(label)}</span></a></li>'
        for icon, label, href in HOME_LINKS)
    rows = "\n".join(
        f'<div class="hours-row{" closed" if time == "விடுமுறை" else ""}" data-row="{"open" if time != "விடுமுறை" else "closed"}">'
        f'<span>{escape(days)}</span><b>{escape(time)}</b></div>'
        for days, time in VISIT_HOURS)
    status_js = f"""<script>
(function () {{
  var box = document.querySelector('.hours'), pill = document.getElementById('hours-status');
  var FROM = {json.dumps(OPEN_FROM)}, UNTIL = {json.dumps(OPEN_UNTIL)}, HOLIDAYS = {json.dumps(GOVT_HOLIDAYS)};
  function mins(s) {{ var a = s.split(':'); return +a[0] * 60 + +a[1]; }}
  function update() {{
    var parts = {{}};
    new Intl.DateTimeFormat('en-GB', {{ timeZone: 'Asia/Kolkata', weekday: 'short', year: 'numeric',
      month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }})
      .formatToParts(new Date()).forEach(function (p) {{ parts[p.type] = p.value; }});
    var date = parts.year + '-' + parts.month + '-' + parts.day;
    var now = (+parts.hour % 24) * 60 + +parts.minute;
    var holiday = parts.weekday === 'Sun' || HOLIDAYS.indexOf(date) !== -1;
    var open = !holiday && now >= mins(FROM) && now < mins(UNTIL);
    box.classList.toggle('is-open', open);
    box.classList.toggle('is-closed', !open);
    pill.textContent = open ? '🟢 இப்போது திறந்திருக்கிறது' : '🔴 இப்போது மூடப்பட்டுள்ளது';
    pill.hidden = false;
    document.querySelectorAll('.hours-row').forEach(function (r) {{
      r.classList.toggle('today', r.getAttribute('data-row') === (holiday ? 'closed' : 'open'));
    }});
  }}
  try {{ update(); setInterval(update, 60000); }} catch (e) {{}}
}})();
</script>"""
    body = f"""<div class="home-wrap">
<header class="hero home-hero">
  <img class="logo" src="images/logo.png" alt="தமிழ்நாடு அரசு சின்னம்" width="88" height="96">
  <h1>{CENTRE_NAME}</h1>
</header>
<main>
<ul class="home-tiles">
{tiles}
</ul>
</main>
<section class="hours" aria-label="வருகை நேரம்">
  <div class="hours-head"><h2>{VISIT_HOURS_TITLE}</h2><span class="hours-status" id="hours-status" hidden></span></div>
{rows}
</section>
</div>
{status_js}
"""
    return HEAD.format(title=CENTRE_NAME, css="style.css", css_version=asset_version("style.css"), goatcounter=GOATCOUNTER) + body + FOOT.format(disclaimer="")


def camp_page():
    """Siddha medical camp page at /camp/ (content to be added)."""
    body = f"""<header class="hero">
  <h1>{CAMP_TITLE}</h1>
  <p class="sub">{CENTRE_NAME}</p>
</header>
<main>
<section><p>முகாம் பற்றிய விவரங்கள் விரைவில் சேர்க்கப்படும்.</p></section>
<nav class="bottombar"><span></span><a class="home" href="../">🏠 முகப்பு</a></nav>
</main>
"""
    return HEAD.format(title=CAMP_TITLE, css="../style.css", css_version=asset_version("style.css"), goatcounter=GOATCOUNTER) + body + FOOT.format(disclaimer="")


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
<h2 class="list-heading">மூலிகைகள் ({len(plants)})</h2>
<ul class="plant-list">
{cards}
</ul>
<nav class="bottombar"><span></span><a class="home" href="../">🏠 முகப்பு</a></nav>
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
    (ROOT / "index.html").write_text(home_page(), encoding="utf-8")
    (ROOT / "camp").mkdir(exist_ok=True)
    (ROOT / "camp" / "index.html").write_text(camp_page(), encoding="utf-8")
    print(f"Built {len(plants)} plant pages.")


if __name__ == "__main__":
    main()

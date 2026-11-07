"""Generate the plant pages from plants.json.

Run:  python build.py
Creates:  index.html  and  plants/<id>/index.html  for every plant.
Uses only the Python standard library.
"""
import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
PLANTS_DIR = ROOT / "plants"

SITE_TITLE = "சித்த மூலிகைக் கண்காட்சி"
DISCLAIMER = "இத்தகவல்கள் விழிப்புணர்வுக்காக மட்டுமே. எந்த மூலிகையையும் பயன்படுத்தும் முன் தகுதியான சித்த மருத்துவரை அணுகவும்."

HEAD = """<!doctype html>
<html lang="ta">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&display=swap">
<link rel="stylesheet" href="{css}">
</head>
<body>
"""

FOOT = """<footer>{disclaimer}</footer>
</body>
</html>
"""


def li_list(items):
    return "\n".join(f"<li>{escape(i)}</li>" for i in items)


def section(heading, body):
    return f'<section><h2>{heading}</h2>{body}</section>' if body else ""


def has_content(p):
    return any(p.get(k) for k in ("facts", "description", "parts_used", "uses", "how_to_use", "caution"))


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


def plant_page(p):
    e = {k: escape(v) if isinstance(v, str) else v for k, v in p.items()}
    img = ""
    if p.get("image") and (ROOT / p["image"]).exists():
        img = f'<img class="photo" src="../../{e["image"]}" alt="{e["tamil_name"]}">'

    body = f"""<header class="hero">
  <a class="back" href="../../">← அனைத்து மூலிகைகள்</a>
  <h1>{e['tamil_name']}</h1>
  <p class="sub">{e['english_name']}{f" · <i>{e['botanical_name']}</i>" if p.get("botanical_name") else ""}</p>
</header>
<main>
{img}
{facts_block(p)}
{section("வேறு பெயர்கள்", f"<p>{e.get('other_names', '')}</p>" if p.get('other_names') else "")}
{section("அறிமுகம்", f"<p>{e['description']}</p>" if p.get("description") else "")}
{"" if has_content(p) else '<section><p>இந்த மூலிகை பற்றிய தகவல்கள் விரைவில் சேர்க்கப்படும்.</p></section>'}
{section("பயன்படும் பாகங்கள்", f'<ul class="chips">{li_list(p.get("parts_used", []))}</ul>' if p.get("parts_used") else "")}
{section("மருத்துவப் பயன்கள்", f"<ul>{li_list(p.get('uses', []))}</ul>" if p.get("uses") else "")}
{section("பயன்படுத்தும் முறை", f"<p>{e['how_to_use']}</p>" if p.get("how_to_use") else "")}
{f'<section class="caution"><h2>⚠ எச்சரிக்கை</h2><p>{e["caution"]}</p></section>' if p.get("caution") else ""}
</main>
"""
    return (HEAD.format(title=f"{e['tamil_name']} – {SITE_TITLE}", css="../../style.css")
            + body + FOOT.format(disclaimer=DISCLAIMER))


def index_page(plants):
    cards = "\n".join(
        f'<li><a href="plants/{escape(p["id"])}/"><strong>{escape(p["tamil_name"])}</strong>'
        f'<span>{escape(p["english_name"])}</span></a></li>'
        for p in plants
    )
    body = f"""<header class="hero"><h1>{SITE_TITLE}</h1>
<p class="sub">ஒவ்வொரு மூலிகையின் அருகில் உள்ள QR குறியீட்டை ஸ்கேன் செய்யவும்</p></header>
<main><ul class="plant-list">
{cards}
</ul></main>
"""
    return HEAD.format(title=SITE_TITLE, css="style.css") + body + FOOT.format(disclaimer=DISCLAIMER)


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

    (ROOT / "index.html").write_text(index_page(plants), encoding="utf-8")
    print(f"Built {len(plants)} plant pages.")


if __name__ == "__main__":
    main()

# Siddha Plants QR Exhibition

Visitors scan the QR sticker on a plant's board and their phone opens that plant's page in Tamil.

- **Live site:** https://siddha-mooligai.github.io/
- **Plant page:** `https://siddha-mooligai.github.io/plants/<id>/`
- **Repository:** https://github.com/siddha-mooligai/siddha-mooligai.github.io (GitHub Pages, branch `main`, root)

## Plants

| # | Plant | id |
|---|---|---|
| 1 | சங்குப்பூ | sangupoo |
| 2 | பிரண்டை | pirandai |
| 3 | மலைவேம்பு | malaivembu |
| 4 | ஆடாதோடை | aadathodai |
| 5 | ஆமணக்கு | aamanaku |
| 6 | புங்கன் | pungu |
| 7 | குப்பைமேனி | kuppaimeni |
| 8 | கற்றாழை | katralai |
| 9 | சீமை அகத்தி | seemaiagathi |
| 10 | நித்யகல்யாணி | nithiyakalyani |
| 11 | பப்பாளி | pappali |
| 12 | வெற்றிலை | vetrilai |
| 13 | இரணக்கள்ளி | iranakalli |
| 14 | வெட்பாலை | vetpalai |
| 15 | பசலைக்கீரை | pasalaikeerai |
| 16 | நந்தியாவட்டம் | nandhiyavattam |
| 17 | கற்பூரவள்ளி | karpooravalli |
| 18 | திருநீற்றுப்பச்சிலை | thiruneetrupachilai |
| 19 | அரளி | arali |
| 20 | நிலவேம்பு | nilavembu |
| 21 | சிற்றரத்தை | sitrarathai |

**Don't change an `id` after the stickers are printed.** The `id` is part of the QR link.

## Files

| File | Purpose |
|---|---|
| `plants.json` | All plant content in Tamil. This is the only file you edit. |
| `build.py` | Turns `plants.json` into the web pages (`index.html`, `plants/<id>/index.html`). |
| `style.css` | Page design. |
| `print-qr.html` | Printable QR cards in the browser (open it on the live site). |
| `tools/make_stickers.py` | Makes passport-size (35 × 45 mm, 600 dpi) QR sticker images. |
| `qr-stickers/` | The sticker images, one per plant, plus a ZIP of all of them. |

## Editing content

Each plant in `plants.json` has these fields:

```json
"facts_heading": "🌸 சங்குப்பூ – உங்களுக்குத் தெரியுமா?",
"facts": [ { "title": "...", "text": "..." } ],
"note_heading": "🌿 சித்த மருத்துவக் குறிப்பு:",
"note": "..."
```

After editing, rebuild and publish:

```
python build.py
git add .
git commit -m "Update content"
git push
```

The site updates in about a minute. The printed QR stickers keep working because their links don't change.
Browsers may show an old copy for up to 10 minutes. Refresh or use a private tab to see the change.

## Photos

Each plant's photo is in `images/<id>.jpg` (about 1000 px, under 200 KB). The current photos come from
Wikimedia Commons under CC BY / CC BY-SA licences. These licences require a credit, so each page shows
one under its photo, taken from the `image_credit` field in `plants.json`.

To use your own photo, replace `images/<id>.jpg` and delete that plant's `image_credit` block, then rebuild.

## Views 👁 and likes 👍

Counts come from **GoatCounter** (free, no cookies). The account is `siddha-mooligai`, and its dashboard is at
https://siddha-mooligai.goatcounter.com.

- Each plant page shows **👁 N பார்வைகள்** in its header (views of that page).
- At the end of each page is **"இந்தத் தகவல் பயனுள்ளதாக இருந்ததா? 👍 ஆம்"**. Each phone can like a plant once,
  and the total shows as "N பேர் விரும்பினர்". Likes are stored in GoatCounter as events named `like-<id>`.
- The GoatCounter setting **"Allow adding visitor counts on your website"** must be ON for the numbers to show.
- To stop your own test visits being counted, open `https://siddha-mooligai.github.io/#toggle-goatcounter` once in your browser.
- If GoatCounter is unreachable or blocked, the numbers are hidden and the page still works.
- The code is in `stats.js`, and the account name is `GOATCOUNTER` in `build.py`.

## Adding a new plant

1. Add an entry to `plants.json` with a new lowercase `id` that has no spaces.
2. Run `python build.py`.
3. Run `python tools/make_stickers.py` to make its sticker. This needs Microsoft Edge and `pip install pillow`.
4. Commit and push.

## Printing the stickers

Send the files in `qr-stickers/` (or the ZIP) to a print shop and say: *passport size 35 × 45 mm, sticker paper, matte, do not crop.*
Laminate the stickers for outdoor boards. Scan every printed sticker with a phone before the exhibition.

# Siddha Plants QR Exhibition

Visitors scan the QR code on a plant's board and their phone opens that plant's page in Tamil.
The site is static and hosted free on **GitHub Pages**.

## How it works

```
plants.json  --(python build.py)-->  plants/<id>/index.html   (one page per plant)
                                     index.html               (list of all plants)
print-qr.html  -> printable QR cards, one per plant, for the boards
```

Each plant's URL looks like this:
`https://<your-github-username>.github.io/<repo-name>/plants/<id>/`

## One-time setup

1. Create a **public** repository on GitHub, e.g. `siddha-plants`.
2. Push this folder to it:
   ```
   git remote add origin https://github.com/<username>/siddha-plants.git
   git branch -M main
   git push -u origin main
   ```
3. On GitHub, go to **Settings → Pages**. Under *Source*, pick **Deploy from a branch**, then branch **main**, folder **/ (root)**, and click **Save**.
4. Wait about a minute. The site is live at `https://<username>.github.io/siddha-plants/`.

## Adding or editing a plant

1. Add a new entry to `plants.json`. Copy an existing entry and change it. The `id` must be
   lowercase English with no spaces (e.g. `nilavembu`). **It becomes the URL, so don't change it after the QR codes are printed.**
2. (Optional) Put a photo at `images/<id>.jpg`. Keep it under about 300 KB so it loads fast on mobile data.
3. Rebuild the pages, then commit and push:
   ```
   python build.py
   git add .
   git commit -m "Add nilavembu"
   git push
   ```

Editing text later is safe: the URL stays the same, so the printed QR codes keep working.

## Printing the QR codes

Open `https://<username>.github.io/siddha-plants/print-qr.html` in a browser and click **Print**.
Each card shows the plant's Tamil name and its QR code.

Tips:
- Print each QR code at least **4 × 4 cm**. Make it bigger if visitors will scan from far away.
- Scan every printed code with a phone before the exhibition.
- To preview on your computer before publishing, run `python -m http.server` in this folder and
  open http://localhost:8000.

## Content note

The sample Tamil text for the 3 plants is only a placeholder. Please have a Siddha practitioner
check all medicinal content before the exhibition.

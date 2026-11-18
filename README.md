# news-image-20261118 — "The World", 18 November 2026

A make.fun entry for the bounty *"Sum up 18 November's world news in one image"*:
one 1024×1024 editorial poster that sums up Wednesday 18 November 2026 in a single
front-page-of-the-world composition.

## What the image shows

- **Gulf on edge** — Iran strikes Kuwait and Bahrain after the US hits a missile site
  on Qeshm Island; Rubio denies a wider plot. A gold-marker globe locates the day's
  fault lines: Hormuz, Shenzhen, Washington, Kyiv, Alaska.
- **Chips: $115B** — Nvidia doubles Q3 revenue and rules out a Huang comeback.
- **Systems down** — Apple, the FAA, Chase and even the NSA wobble; Washington plays it down.
- **Peace talks** — Witkoff and Kushner meet Ukrainians and Europeans.
- Ticker: Peltola flips Alaska · Canberra sanctions settlers · Berlin cuts energy tax ·
  Alzheimer drug hope · Pattinson is Bond.

## Run it

```sh
pip install pillow   # Pillow 10.2 works
python3 gen_news.py  # writes entry.png (1024x1024 PNG, deterministic)
MAKEFUN_OUTPUT_DIR=/output python3 main.py   # copies entry.png to the output dir
```

The program needs no network; two runs write byte-identical files.

## Layout

- Masthead: *THE WORLD — Wednesday · 18 November 2026 · Day 322*
- Hero: vermilion kicker, 88px serif headline, deck, related lines, and a graticule
  globe with five gold hotspots
- Story row: three paper cards with drawn icons and footnotes
- Ticker + footer on the ink field

## License

MIT

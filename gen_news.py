#!/usr/bin/env python3
"""
gen_news.py - one image that sums up Wednesday 18 November 2026's world news.

A 1024x1024 editorial "front page of the world" poster, rendered with Pillow.
No network, fully deterministic output.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
MARGIN = 48

INK = (11, 16, 32)          # #0B1020 deep ink navy
INK_SOFT = (24, 33, 54)     # lighter navy for globe fill
PAPER = (242, 237, 228)     # #F2EDE4 warm paper
PAPER_DIM = (228, 222, 209)
VERMILION = (214, 64, 43)   # #D6402B
GOLD = (232, 184, 75)       # #E8B84B
SLATE = (138, 147, 168)     # #8A93A8
SLATE_DARK = (74, 82, 100)
INK_ON_PAPER = (24, 29, 46)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def text_w(draw, text, f):
    return draw.textlength(text, font=f)


def fit_size(draw, text, path, max_size, max_width, min_size=8):
    size = max_size
    while size > min_size:
        if text_w(draw, text, font(path, size)) <= max_width:
            return size
        size -= 1
    return min_size


def spaced(draw, text, x, y, f, fill, tracking):
    """Draw letter-spaced text; returns the width it used."""
    cx = x
    for ch in text:
        draw.text((cx, y), ch, fill=fill, font=f)
        cx += text_w(draw, ch, f) + tracking
    return cx - x - tracking


def spaced_center(draw, text, cx, y, f, fill, tracking):
    w = text_w(draw, text, f) + tracking * (len(text) - 1)
    spaced(draw, text, cx - w / 2, y, f, fill, tracking)


def wrap(draw, text, f, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, f) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def shadow_rect(layer, box, offset=4, blur=6, alpha=110):
    """Soft drop shadow drawn on an RGBA layer."""
    sh = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    sh.rectangle([x0 + offset, y0 + offset, x1 + offset, y1 + offset],
                 fill=(0, 0, 0, alpha))
    return layer.filter  # caller blurs explicitly


def paper_panel(base, layer_draw, box, keyline=True):
    x0, y0, x1, y1 = box
    layer_draw.rectangle([x0 + 5, y0 + 6, x1 + 5, y1 + 6], fill=(0, 0, 0, 120))
    # warm gradient fill (subtle vertical)
    for i, yy in enumerate(range(y0, y1)):
        t = i / max(1, (y1 - y0))
        c = tuple(int(a + (b - a) * t) for a, b in zip((247, 243, 235), (236, 229, 216)))
        layer_draw.line([(x0, yy), (x1, yy)], fill=c)
    if keyline:
        layer_draw.rectangle([x0, y0, x1, y1], outline=GOLD + (255,), width=2)
        layer_draw.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4],
                             outline=(0, 0, 0, 40), width=1)


def draw_background(draw):
    # soft vignette on the ink background
    for i in range(140):
        t = i / 140
        a = int(26 * (1 - t))
        inset = int(t * 380)
        draw.rectangle([inset, inset, CANVAS - inset, CANVAS - inset],
                       outline=(255, 255, 255, a) if False else (5, 8, 18))
    # faint halftone over ink only
    for x in range(0, CANVAS, 14):
        for y in range(0, CANVAS, 14):
            if (x // 14 + y // 14) % 2 == 0:
                draw.point((x, y), fill=(20, 27, 45))


def draw_masthead(draw):
    draw.rectangle([MARGIN, 24, CANVAS - MARGIN, 25], fill=GOLD)
    draw.rectangle([MARGIN, 29, CANVAS - MARGIN, 29], fill=GOLD)

    f = font(SERIF_BOLD, 62)
    spaced_center(draw, "THE WORLD", CANVAS / 2, 38, f, PAPER, 6)

    sub = "WEDNESDAY  ·  18 NOVEMBER 2026  ·  DAY 322"
    fs = font(SANS_BOLD, 13)
    spaced_center(draw, sub, CANVAS / 2, 110, fs, SLATE, 3)

    fm = font(SANS, 11)
    draw.text((MARGIN, 110), "No. 322", fill=SLATE_DARK, font=fm)
    w = text_w(draw, "make.fun picture desk", fm)
    draw.text((CANVAS - MARGIN - w, 110), "make.fun picture desk",
              fill=SLATE_DARK, font=fm)

    draw.rectangle([MARGIN, 132, CANVAS - MARGIN, 132], fill=GOLD)


def draw_globe(base, cx, cy, r):
    layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # sphere with radial-ish gradient: concentric filled discs
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        shade = int(14 + 26 * (1 - t))
        rr = int(r * t)
        ox = int((1 - t) * -8)
        oy = int((1 - t) * -8)
        col = (shade + 6, shade + 10, shade + 22, 255)
        d.ellipse([cx - rr + ox, cy - rr + oy, cx + rr + ox, cy + rr + oy], fill=col)

    # meridians: full ellipses of varying width
    for lon in (-60, -30, 0, 30, 60):
        rx = int(r * math.cos(math.radians(lon)))
        d.ellipse([cx - rx, cy - r, cx + rx, cy + r],
                  outline=(96, 106, 128, 170), width=1)
    # equator
    d.line([cx - r, cy, cx + r, cy], fill=(96, 106, 128, 170), width=1)
    # latitude chords
    for lat in (-60, -30, 30, 60):
        y0 = cy + int(r * math.sin(math.radians(lat)))
        half = int(r * math.cos(math.radians(lat)))
        ry = max(3, int(r * 0.05))
        d.ellipse([cx - half, y0 - ry, cx + half, y0 + ry],
                  outline=(96, 106, 128, 150), width=1)

    # terminator: darker right limb
    d.pieslice([cx - r, cy - r, cx + r, cy + r], -90, 90, fill=(4, 7, 16, 110))
    # re-draw meridian arcs lightly over terminator
    for lon in (-60, -30, 0, 30, 60):
        rx = int(r * math.cos(math.radians(lon)))
        d.arc([cx - rx, cy - r, cx + rx, cy + r], 270, 90,
              fill=(78, 86, 104, 120), width=1)
    d.arc([cx - r, cy - r, cx + r, cy + r], 270, 90, fill=(78, 86, 104, 120), width=1)
    for lat in (-60, -30, 30, 60):
        y0 = cy + int(r * math.sin(math.radians(lat)))
        half = int(r * math.cos(math.radians(lat)))
        ry = max(3, int(r * 0.05))
        d.arc([cx - half, y0 - ry, cx + half, y0 + ry], 270, 90,
              fill=(78, 86, 104, 100), width=1)

    # outer gold ring
    d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6],
              outline=GOLD + (255,), width=2)
    d.ellipse([cx - r - 12, cy - r - 12, cx + r + 12, cy + r + 12],
              outline=(232, 184, 75, 70), width=1)

    base.alpha_composite(layer)

    # hotspots (on the base, crisp)
    markers = [
        (0.06, -0.62, "WASHINGTON"),
        (-0.70, -0.50, "ALASKA"),
        (-0.50, -0.16, "KYIV"),
        (0.20, 0.46, "HORMUZ"),
        (0.64, 0.26, "SHENZHEN"),
    ]
    fl = font(SANS_BOLD, 11)
    dd = ImageDraw.Draw(base)
    for u, v, label in markers:
        mx = cx + u * r
        my = cy + v * r
        dd.ellipse([mx - 7, my - 7, mx + 7, my + 7],
                   outline=GOLD, width=2)
        dd.ellipse([mx - 3, my - 3, mx + 3, my + 3], fill=GOLD)
        lx = mx + 12 if u >= -0.3 else mx - 12 - text_w(dd, label, fl)
        ly = my - 6
        dd.text((lx + 1, ly + 1), label, fill=(0, 0, 0), font=fl)
        dd.text((lx, ly), label, fill=GOLD, font=fl)


def draw_hero(draw, base):
    top, bottom = 150, 548
    left = MARGIN
    right = left + 560

    panel = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    paper_panel(base, pd, (left, top, right, bottom))
    base.alpha_composite(panel)

    x0 = left + 26
    # kicker
    fk = font(SANS_BOLD, 15)
    draw.rectangle([x0, top + 20, x0 + 12, top + 32], fill=VERMILION)
    spaced(draw, "GULF  ·  ESCALATION", x0 + 20, top + 18, fk, VERMILION, 2)

    # headline
    fh = font(SERIF_BOLD, 88)
    draw.text((x0 - 3, top + 48), "GULF ON", fill=INK_ON_PAPER, font=fh)
    draw.text((x0 - 3, top + 134), "EDGE", fill=VERMILION, font=fh)

    # deck
    fd = font(SERIF, 19)
    deck = ("Iran strikes Kuwait and Bahrain after the US hits a Qeshm "
            "Island missile site; Rubio denies a wider plot.")
    y = top + 236
    for line in wrap(draw, deck, fd, right - x0 - 26):
        draw.text((x0, y), line, fill=(58, 66, 86), font=fd)
        y += 25

    # rule
    draw.rectangle([x0, y + 4, right - 26, y + 5], fill=(196, 189, 175))

    # related lines
    fr = font(SANS_BOLD, 14)
    ry = y + 20
    for label in ("Shenzhen: Xi and Putin ahead of Trump's trilateral",
                  "Quad returns in Manila after two years"):
        draw.polygon([(x0 + 5, ry + 7), (x0 + 11, ry + 12), (x0 + 5, ry + 17),
                      (x0 - 1, ry + 12)], fill=GOLD)
        draw.text((x0 + 20, ry), label, fill=(58, 66, 86), font=fr)
        ry += 22

    draw_globe(base, 806, 352, 132)


def draw_story_row(draw, base):
    top, bottom = 578, 806
    gap = 20
    card_w = (CANVAS - 2 * MARGIN - 2 * gap) // 3
    xs = [MARGIN + i * (card_w + gap) for i in range(3)]

    panel = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    for x in xs:
        paper_panel(base, pd, (x, top, x + card_w, bottom), keyline=False)
        pd.rectangle([x, top, x + card_w, bottom], outline=(196, 189, 175, 255), width=1)
        pd.rectangle([x, top, x + card_w, top + 3], fill=GOLD + (255,))
    base.alpha_composite(panel)

    stories = [
        ("CHIPS: $115B", ["Nvidia doubles Q3 revenue to $115bn,",
                          "beats forecasts — and rules out a",
                          "comeback for Jensen Huang."],
         "chip", "Q3 REVENUE  ·  x2 YEAR ON YEAR"),
        ("SYSTEMS DOWN", ["Apple, the FAA, Chase and even the",
                          "NSA all wobble in a wave of outages;",
                          "Washington plays it down."],
         "globe", "OUTAGES  ·  DAY 3 OF THE WAVE"),
        ("PEACE TALKS", ["Witkoff and Kushner sit with",
                         "Ukrainians and Europeans; the",
                         "Kremlin signals Europe may join."],
         "talks", "ENVOYS  ·  GENEVA, THURSDAY"),
    ]

    fh = font(SANS_BOLD, 20)
    fb = font(SANS, 14)
    fstat = font(SANS_BOLD, 11)
    for x, (head, body, icon, stat) in zip(xs, stories):
        ix, iy = x + 24, top + 26
        if icon == "chip":
            s = 40
            draw.rectangle([ix, iy, ix + s, iy + s], outline=INK_ON_PAPER, width=3)
            draw.rectangle([ix + 9, iy + 9, ix + s - 9, iy + s - 9],
                           outline=INK_ON_PAPER, width=2)
            draw.rectangle([ix + 16, iy + 16, ix + s - 16, iy + s - 16], fill=VERMILION)
            for k in range(3):
                p = ix + 7 + k * 12
                draw.line([(p, iy - 5), (p, iy)], fill=INK_ON_PAPER, width=2)
                draw.line([(p, iy + s), (p, iy + s + 5)], fill=INK_ON_PAPER, width=2)
                draw.line([(ix - 5, iy + 8 + k * 10), (ix, iy + 8 + k * 10)],
                          fill=INK_ON_PAPER, width=2)
                draw.line([(ix + s, iy + 8 + k * 10), (ix + s + 5, iy + 8 + k * 10)],
                          fill=INK_ON_PAPER, width=2)
        elif icon == "globe":
            s = 40
            draw.ellipse([ix, iy, ix + s, iy + s], outline=INK_ON_PAPER, width=3)
            draw.ellipse([ix + 9, iy, ix + s - 9, iy + s], outline=INK_ON_PAPER, width=2)
            draw.line([ix + s + 6, iy - 6, ix - 6, iy + s + 6], fill=VERMILION, width=4)
        else:
            s = 40
            draw.rectangle([ix - 2, iy + s + 2, ix + s + 2, iy + s + 6],
                           fill=INK_ON_PAPER)
            draw.ellipse([ix - 2, iy, ix + s // 2 + 4, iy + s - 4],
                         outline=INK_ON_PAPER, width=3)
            draw.ellipse([ix + s // 2 - 4, iy, ix + s + 2, iy + s - 4],
                         outline=INK_ON_PAPER, width=3)
            draw.ellipse([ix + s // 2 - 5, iy + 14, ix + s // 2 + 5, iy + 24],
                         fill=VERMILION)

        draw.text((ix + 60, iy + 6), head, fill=INK_ON_PAPER, font=fh)
        by = top + 92
        for line in body:
            draw.text((x + 24, by), line, fill=(84, 92, 110), font=fb)
            by += 22
        # small stat line at the card foot
        draw.rectangle([x + 24, bottom - 34, x + 60, bottom - 33], fill=GOLD)
        draw.text((x + 68, bottom - 42), stat, fill=SLATE_DARK, font=fstat)


def draw_ticker(draw):
    items = ["PELTOLA FLIPS ALASKA", "CANBERRA SANCTIONS SETTLERS",
             "BERLIN CUTS ENERGY TAX", "ALZHEIMER DRUG HOPE", "PATTINSON IS BOND"]
    fs = 14
    diamond = "  ◆  "
    while fs > 9:
        f = font(SANS_BOLD, fs)
        sep_w = text_w(draw, diamond, f)
        total = MARGIN
        for it in items:
            total += text_w(draw, it, f) + sep_w
        total -= sep_w
        if total <= CANVAS - MARGIN:
            break
        fs -= 1
    y = 902
    draw.rectangle([MARGIN, 872, CANVAS - MARGIN, 873], fill=GOLD)
    # live dot
    draw.ellipse([MARGIN + 1, y + 6, MARGIN + 13, y + 18], fill=VERMILION)
    cx = MARGIN + 24
    f = font(SANS_BOLD, fs)
    for i, it in enumerate(items):
        draw.text((cx, y), it, fill=(168, 176, 196), font=f)
        cx += text_w(draw, it, f)
        if i < len(items) - 1:
            w = text_w(draw, diamond, f)
            dd = font(SANS_BOLD, fs - 2)
            dw = text_w(draw, "◆", dd)
            draw.text((cx + (w - dw) / 2, y + 2), "◆", fill=GOLD, font=dd)
            cx += w


def draw_footer(draw):
    draw.rectangle([MARGIN, 964, CANVAS - MARGIN, 964], fill=(58, 66, 86))
    ft = "ONE DAY  ·  ONE PICTURE  —  18.XI.2026"
    f = font(SANS, 11)
    w = text_w(draw, ft, f)
    spaced_center(draw, ft, CANVAS / 2, 976, f, SLATE_DARK, 1)


def main():
    base = Image.new("RGBA", (CANVAS, CANVAS), INK + (255,))
    draw = ImageDraw.Draw(base)

    draw_background(draw)
    draw_masthead(draw)
    draw_hero(draw, base)
    draw_story_row(draw, base)
    draw_ticker(draw)
    draw_footer(draw)

    out = base.convert("RGB")
    out.save("entry.png", "PNG")

    size = os.path.getsize("entry.png")
    with Image.open("entry.png") as img:
        print(f"Generated entry.png: {img.size[0]}x{img.size[1]} {img.format}, {size} bytes")
    print(f"Under 1MiB: {'Yes' if size < 1048576 else 'No'}")


if __name__ == "__main__":
    main()

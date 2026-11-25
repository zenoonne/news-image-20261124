#!/usr/bin/env python3
"""Render the front page for the news-image-20261124 make.fun bounty.

One square, 1024x1024, drawn entirely with Pillow primitives (no network,
no external images).  Deterministic: same bytes on every run.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

import worldmap

W = H = 1024
MARGIN = 10

# ----------------------------------------------------------------------------
# palette
# ----------------------------------------------------------------------------
PAPER = (247, 243, 232)
INK = (22, 22, 22)
RULE = (34, 34, 34)
GREY = (110, 110, 110)
LIGHT = (232, 226, 212)

REGION = {
    "EU": ((38, 84, 168), "EUROPE"),
    "AS": ((176, 48, 48), "ASIA"),
    "AM": ((32, 118, 74), "AMERICAS"),
    "AF": ((196, 120, 22), "AFRICA"),
    "ME": ((122, 60, 152), "MIDDLE EAST"),
    "WO": ((78, 78, 78), "WORLD"),
}

TAG = {
    "REPORTED": (32, 108, 58),
    "FORECAST": (30, 78, 158),
    "CLAIM": (168, 92, 20),
}

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_S = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


# ----------------------------------------------------------------------------
# small drawing helpers
# ----------------------------------------------------------------------------
def text(d, xy, s, f, fill=INK, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def scene_label(d, x0, y0, label, fill, bg):
    """Scene corner label on a clean patch of the scene background."""
    f = font(FONT_B, 10)
    tw = d.textlength(label, font=f)
    d.rectangle((x0 + 2, y0 + 1, x0 + 2 + tw + 10, y0 + 18), fill=bg)
    text(d, (x0 + 6, y0 + 5), label, f, fill)


def wrap(d, s, f, maxw):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(d, xy, s, f, maxw, leading, fill=INK, maxlines=None):
    x, y = xy
    lines = wrap(d, s, f, maxw)
    if maxlines:
        lines = lines[:maxlines]
    for i, ln in enumerate(lines):
        text(d, (x, y + i * leading), ln, f, fill)
    return y + len(lines) * leading


def box(d, r, fill=None, outline=None, width=1):
    if fill is not None:
        d.rectangle(r, fill=fill)
    if outline is not None:
        d.rectangle(r, outline=outline, width=width)


def tag(d, xy, label):
    """Small coloured confidence badge."""
    f = font(FONT_B, 10)
    tw = d.textlength(label, font=f)
    x, y = xy
    d.rectangle((x, y, x + tw + 10, y + 13), fill=TAG[label])
    text(d, (x + 5, y + 1), label, f, (255, 255, 255))


def region_tag(d, xy, code):
    col, name = REGION[code]
    f = font(FONT_B, 10)
    tw = d.textlength(name, font=f)
    x, y = xy
    d.rectangle((x, y, x + tw + 10, y + 13), fill=col)
    text(d, (x + 5, y + 1), name, f, (255, 255, 255))
    return x + tw + 12


# ----------------------------------------------------------------------------
# flat-cartoon scene illustrations (several elements each, no external art)
# ----------------------------------------------------------------------------
def scene_zaporizhzhia(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    # night sky
    d.rectangle(r, fill=(28, 34, 58))
    d.ellipse((x0 + w * 0.72, y0 + 6, x0 + w * 0.72 + 22, y0 + 28), fill=(240, 226, 150))
    # stars
    for fx, fy in ((0.12, 0.18), (0.3, 0.1), (0.55, 0.22), (0.88, 0.3), (0.42, 0.3)):
        d.ellipse((x0 + w * fx, y0 + h * fy, x0 + w * fx + 3, y0 + h * fy + 3), fill=(230, 230, 210))
    # ground
    d.rectangle((x0, y1 - h * 0.22, x1, y1), fill=(60, 52, 44))
    # damaged 5-storey block
    bx0 = x0 + w * 0.10
    bx1 = x0 + w * 0.62
    by0 = y0 + h * 0.16
    by1 = y1 - h * 0.22
    d.rectangle((bx0, by0, bx1, by1), fill=(150, 146, 138), outline=(60, 58, 54))
    rows = 5
    cols = 3
    for i in range(rows):
        for j in range(cols):
            wx = bx0 + 8 + j * (bx1 - bx0 - 16) / cols
            wy = by0 + 8 + i * (by1 - by0 - 16) / rows
            ww = (bx1 - bx0 - 16) / cols - 8
            wh = (by1 - by0 - 16) / rows - 8
            lit = (i + j) % 3 != 0
            d.rectangle((wx, wy, wx + ww, wy + wh),
                        fill=(250, 214, 120) if lit else (40, 40, 44))
    # blown-out top corner + smoke
    d.polygon([(bx0 + 6, by0 + 6), (bx1 - 40, by0 + 6), (bx0 + 6, by0 + 44)], fill=(40, 36, 34))
    for k, rad in enumerate((26, 20, 14)):
        cx = bx0 + w * 0.06 + k * 10
        cy = by0 - h * 0.06 + k * 8
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(90, 88, 90))
    # missile streak from the corner
    d.line((x0 + w * 0.98, y0 + h * 0.04, bx0 + w * 0.04, by0 + h * 0.08),
           fill=(255, 150, 60), width=3)
    # rubble
    for fx in (0.2, 0.32, 0.5, 0.62):
        rx = x0 + w * fx
        d.rectangle((rx, y1 - h * 0.20, rx + 10, y1 - h * 0.13), fill=(120, 112, 104))
    # rescue worker
    px = x0 + w * 0.78
    py = y1 - h * 0.30
    d.ellipse((px - 6, py - 18, px + 6, py - 6), fill=(240, 208, 170))
    d.rectangle((px - 7, py - 6, px + 7, py + 14), fill=(240, 190, 40))  # hi-vis
    d.rectangle((px - 9, py - 20, px + 9, py - 16), fill=(240, 200, 60))  # helmet
    # Ukraine flag
    fw = 34
    fx = x1 - fw - 10
    fy = y1 - h * 0.20
    d.rectangle((fx, fy, fx + fw, fy + 12), fill=(38, 90, 200))
    d.rectangle((fx, fy + 12, fx + fw, fy + 24), fill=(244, 214, 40))
    d.line((fx - 4, fy, fx - 4, fy + 26), fill=(200, 200, 200), width=2)
    text(d, (fx + 2, fy + 2), "UA", font(FONT_B, 9), (255, 255, 255))


def scene_markets(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(24, 26, 34))
    # wall screen with a falling line
    sx0, sy0 = x0 + w * 0.08, y0 + h * 0.10
    sx1, sy1 = x0 + w * 0.92, y0 + h * 0.60
    d.rectangle((sx0, sy0, sx1, sy1), fill=(12, 14, 20), outline=(90, 96, 110))
    pts = [(0.0, 0.35), (0.18, 0.25), (0.34, 0.45), (0.5, 0.4), (0.66, 0.7), (0.82, 0.62), (1.0, 0.92)]
    poly = [(sx0 + (sx1 - sx0) * fx, sy0 + (sy1 - sy0) * fy) for fx, fy in pts]
    d.line(poly, fill=(240, 70, 70), width=3)
    for p in poly:
        d.ellipse((p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3), fill=(240, 70, 70))
    text(d, (sx0 + 6, sy0 + 4), "NVDA  -7.7%", font(FONT_B, 13), (255, 120, 120))
    # big red down arrow
    ax = x1 - 30
    d.polygon([(ax - 12, y0 + h * 0.18), (ax + 12, y0 + h * 0.18), (ax, y0 + h * 0.42)], fill=(235, 70, 70))
    d.rectangle((ax - 5, y0 + h * 0.08, ax + 5, y0 + h * 0.18), fill=(235, 70, 70))
    # trading desk
    d.rectangle((x0, y1 - h * 0.26, x1, y1 - h * 0.14), fill=(70, 60, 48))
    # two traders
    for k, fx in enumerate((0.28, 0.62)):
        px = x0 + w * fx
        py = y1 - h * 0.26
        d.ellipse((px - 7, py - 26, px + 7, py - 12), fill=(238, 206, 168))
        d.rectangle((px - 9, py - 12, px + 9, py + 14), fill=(150, 60, 60) if k == 0 else (60, 90, 150))
    # chip
    cx = x0 + w * 0.16
    cy = y1 - h * 0.10
    d.rectangle((cx - 14, cy - 8, cx + 14, cy + 8), fill=(60, 66, 60), outline=(180, 190, 180))
    for i in range(4):
        d.line((cx - 14, cy - 6 + i * 4, cx - 20, cy - 6 + i * 4), fill=(200, 200, 160), width=1)
        d.line((cx + 14, cy - 6 + i * 4, cx + 20, cy - 6 + i * 4), fill=(200, 200, 160), width=1)
    text(d, (x0 + w * 0.30, y1 - h * 0.12), "AI SELL-OFF", font(FONT_B, 12), (250, 250, 250))


def scene_hormuz(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    # dusk sky
    d.rectangle((x0, y0, x1, y0 + h * 0.5), fill=(70, 60, 90))
    textile = (56, 70, 96)
    d.rectangle((x0, y0 + h * 0.5, x1, y1), fill=textile)  # sea
    # sun low
    d.ellipse((x1 - 60, y0 + h * 0.30, x1 - 20, y0 + h * 0.48), fill=(240, 170, 90))
    # distant coast
    d.polygon([(x0, y0 + h * 0.5), (x0 + w * 0.3, y0 + h * 0.40),
               (x0 + w * 0.55, y0 + h * 0.50)], fill=(90, 78, 70))
    # tanker hull
    hx0 = x0 + w * 0.18
    hx1 = x0 + w * 0.74
    hy = y0 + h * 0.66
    d.polygon([(hx0, hy), (hx1, hy), (hx1 - 12, hy + 20), (hx0 + 12, hy + 20)], fill=(40, 44, 50))
    d.rectangle((hx0 + 30, hy - 12, hx1 - 34, hy), fill=(150, 60, 40))  # deck housing
    # fire + smoke on the tanker
    fx = hx0 + (hx1 - hx0) * 0.4
    for k, rad in enumerate((22, 16, 10)):
        d.ellipse((fx - rad + k * 6, hy - 34 - k * 8, fx + rad + k * 6, hy - 34 - k * 8 + rad * 2),
                  fill=(250, 150, 40) if k == 0 else (120, 110, 110))
    # waves
    for i in range(3):
        wy = y1 - 16 + i * 5
        d.line((x0 + 6 + i * 12, wy, x1 - 10, wy), fill=(96, 116, 150), width=2)
    # floating mines
    for fx, fy in ((0.14, 0.84), (0.5, 0.9), (0.84, 0.82)):
        mx, my = x0 + w * fx, y0 + h * fy
        d.ellipse((mx - 8, my - 8, mx + 8, my + 8), fill=(30, 30, 34), outline=(230, 120, 40))
        for a in range(8):
            import math
            ang = a * math.pi / 4
            d.line((mx + 8 * math.cos(ang), my + 8 * math.sin(ang),
                    mx + 13 * math.cos(ang), my + 13 * math.sin(ang)), fill=(230, 120, 40), width=1)
    text(d, (x0 + 8, y0 + 6), "STRAIT OF HORMUZ", font(FONT_B, 11), (240, 230, 200))


def _mini_flag(d, x, y, w, h, bands, vertical=False):
    if vertical:
        n = len(bands)
        for i, c in enumerate(bands):
            d.rectangle((x + i * w / n, y, x + (i + 1) * w / n, y + h), fill=c)
    else:
        n = len(bands)
        for i, c in enumerate(bands):
            d.rectangle((x, y + i * h / n, x + w, y + (i + 1) * h / n), fill=c)


def scene_afcon(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(196, 226, 200))
    # pitch stripes
    d.rectangle((x0, y1 - h * 0.34, x1, y1), fill=(60, 150, 70))
    # trophy
    cx = x0 + w * 0.32
    cy = y0 + h * 0.52
    d.ellipse((cx - 14, cy - 16, cx + 14, cy + 12), fill=(228, 190, 60), outline=(150, 110, 20))
    d.rectangle((cx - 4, cy + 10, cx + 4, cy + 22), fill=(200, 160, 40))
    d.rectangle((cx - 12, cy + 22, cx + 12, cy + 27), fill=(170, 130, 30))
    d.arc((cx - 20, cy - 20, cx - 6, cy + 4), 90, 270, fill=(200, 160, 40), width=3)
    d.arc((cx + 6, cy - 20, cx + 20, cy + 4), -90, 90, fill=(200, 160, 40), width=3)
    d.ellipse((cx - 8, cy - 10, cx + 8, cy + 6), fill=(250, 235, 150))
    # flag
    _mini_flag(d, x1 - 40, y0 + 8, 30, 20, [(0, 130, 60), (250, 220, 40), (200, 40, 40)], vertical=True)
    # ball
    bx = x0 + w * 0.62
    by = y1 - h * 0.24
    d.ellipse((bx - 12, by - 12, bx + 12, by + 12), fill=(250, 250, 250), outline=(40, 40, 40))
    scene_label(d, x0, y0, "CHAMPIONS", (20, 90, 40), (196, 226, 200))


def scene_gaza(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(214, 196, 160))
    d.rectangle((x0, y1 - h * 0.3, x1, y1), fill=(180, 160, 128))
    # damaged buildings
    for fx, fh in ((0.1, 0.55), (0.4, 0.75), (0.7, 0.45)):
        bx = x0 + w * fx
        d.rectangle((bx, y1 - h * 0.3 - h * fh, bx + w * 0.2, y1 - h * 0.3),
                    fill=(160, 152, 140), outline=(90, 84, 78))
    # smoke
    for k, rad in enumerate((14, 10)):
        cxx = x0 + w * 0.5 + k * 6
        d.ellipse((cxx - rad, y1 - h * 0.3 - h * 0.75 - k * 6, cxx + rad, y1 - h * 0.3 - h * 0.75 - k * 6 + rad * 2),
                  fill=(110, 108, 106))
    # flag (Palestinian)
    _mini_flag(d, x1 - 34, y0 + 6, 26, 17, [(20, 20, 20), (250, 250, 250), (30, 130, 60)])
    scene_label(d, x0, y0, "GAZA", (60, 40, 20), (214, 196, 160))


def scene_bangladesh(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(222, 214, 190))
    d.rectangle((x0, y1 - h * 0.28, x1, y1), fill=(120, 128, 120))
    # tear-gas cloud
    for k, rad in enumerate((18, 13, 9)):
        d.ellipse((x0 + 10 + k * 10, y0 + 8 + k * 4, x0 + 10 + k * 10 + rad, y0 + 8 + k * 4 + rad),
                  fill=(226, 226, 220))
    # crowd of protesters
    for i, fx in enumerate((0.32, 0.46, 0.60, 0.74)):
        px = x0 + w * fx
        py = y1 - h * 0.28
        d.ellipse((px - 5, py - 26, px + 5, py - 16), fill=(238, 206, 168))
        d.rectangle((px - 6, py - 16, px + 6, py + 6), fill=(60, 90, 140))
        d.line((px - 6, py - 12, px - 12, py - 26), fill=(60, 90, 140), width=3)
        d.line((px + 6, py - 12, px + 12, py - 26), fill=(60, 90, 140), width=3)
    scene_label(d, x0, y0, "DHAKA", (60, 40, 20), (222, 214, 190))


def scene_hasina(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(180, 208, 232))
    for fx in (0.6, 0.8):
        d.ellipse((x0 + w * fx, y0 + 8, x0 + w * fx + 30, y0 + 30), fill=(240, 240, 240))
    # plane
    d.polygon([(x0 + w * 0.1, y0 + h * 0.46), (x0 + w * 0.62, y0 + h * 0.42),
               (x0 + w * 0.62, y0 + h * 0.54), (x0 + w * 0.1, y0 + h * 0.5)], fill=(230, 230, 235))
    d.polygon([(x0 + w * 0.3, y0 + h * 0.5), (x0 + w * 0.42, y0 + h * 0.74),
               (x0 + w * 0.5, y0 + h * 0.74), (x0 + w * 0.44, y0 + h * 0.5)], fill=(200, 200, 210))
    d.ellipse((x0 + w * 0.06, y0 + h * 0.42, x0 + w * 0.13, y0 + h * 0.54), fill=(120, 170, 220))
    # Bangladesh flag
    d.rectangle((x1 - 34, y0 + 6, x1 - 6, y0 + 26), fill=(0, 106, 78))
    d.ellipse((x1 - 24, y0 + 11, x1 - 14, y0 + 21), fill=(244, 60, 60))
    scene_label(d, x0, y0, "HOME", (20, 40, 70), (180, 208, 232))


def scene_cartagena(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(240, 226, 190))
    d.rectangle((x0, y0 + h * 0.2, x1, y0 + h * 0.75), fill=(228, 208, 170))
    # storefront awning
    for i in range(6):
        col = (200, 60, 60) if i % 2 == 0 else (240, 240, 240)
        d.rectangle((x0 + 6 + i * (w - 12) / 6, y0 + h * 0.22, x0 + 6 + (i + 1) * (w - 12) / 6, y0 + h * 0.34), fill=col)
    d.rectangle((x0 + 10, y0 + h * 0.36, x1 - 10, y0 + h * 0.72), fill=(150, 190, 205))
    # figures (hostage standoff)
    for fx, col in ((0.3, (60, 60, 70)), (0.5, (200, 170, 40)), (0.7, (60, 60, 70))):
        px = x0 + w * fx
        py = y1 - h * 0.1
        d.ellipse((px - 6, py - 28, px + 6, py - 16), fill=(236, 200, 160))
        d.rectangle((px - 7, py - 16, px + 7, py + 8), fill=col)
    scene_label(d, x0, y0, "CARTAGENA", (60, 40, 20), (240, 226, 190))


def scene_femicide(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(38, 44, 74))
    # UN-blue band
    d.rectangle((x0, y0 + h * 0.62, x1, y1), fill=(60, 120, 190))
    # candle
    cx = x0 + w * 0.3
    d.rectangle((cx - 8, y0 + h * 0.4, cx + 8, y0 + h * 0.86), fill=(240, 236, 220))
    d.ellipse((cx - 5, y0 + h * 0.28, cx + 5, y0 + h * 0.42), fill=(250, 180, 60))
    d.ellipse((cx - 2, y0 + h * 0.32, cx + 2, y0 + h * 0.40), fill=(255, 240, 180))
    # figure with raised hand
    px = x0 + w * 0.66
    py = y0 + h * 0.6
    d.ellipse((px - 8, py - 30, px + 8, py - 14), fill=(238, 206, 168))
    d.polygon([(px - 12, py - 14), (px + 12, py - 14), (px + 10, py + 20), (px - 10, py + 20)], fill=(240, 240, 240))
    d.line((px + 10, py - 10, px + 24, py - 30), fill=(240, 240, 240), width=4)
    scene_label(d, x0, y0, "1 EVERY 10 MIN", (255, 210, 120), (38, 44, 74))


def scene_ukheat(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(236, 176, 96))
    # sun
    cx, cy = x0 + w * 0.26, y0 + h * 0.4
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=(250, 220, 90))
    for a in range(8):
        import math
        ang = a * math.pi / 4
        d.line((cx + 18 * math.cos(ang), cy + 18 * math.sin(ang),
                cx + 26 * math.cos(ang), cy + 26 * math.sin(ang)), fill=(250, 220, 90), width=2)
    # thermometer
    tx = x0 + w * 0.62
    d.rectangle((tx - 5, y0 + h * 0.2, tx + 5, y0 + h * 0.72), fill=(240, 240, 240), outline=(80, 80, 80))
    d.ellipse((tx - 10, y0 + h * 0.7, tx + 10, y0 + h * 0.9), fill=(220, 60, 60))
    d.rectangle((tx - 3, y0 + h * 0.34, tx + 3, y0 + h * 0.72), fill=(220, 60, 60))
    scene_label(d, x0, y0, "5,258 DEATHS", (120, 40, 20), (236, 176, 96))


def scene_chess(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(60, 54, 46))
    # board
    bx0, by0 = x0 + w * 0.1, y0 + h * 0.12
    bx1, by1 = x0 + w * 0.72, y1 - h * 0.08
    n = 4
    for i in range(n):
        for j in range(n):
            c = (235, 225, 205) if (i + j) % 2 == 0 else (110, 90, 70)
            d.rectangle((bx0 + i * (bx1 - bx0) / n, by0 + j * (by1 - by0) / n,
                         bx0 + (i + 1) * (bx1 - bx0) / n, by0 + (j + 1) * (by1 - by0) / n), fill=c)
    # king
    kx = bx0 + (bx1 - bx0) * 0.62
    ky = by0 + (by1 - by0) * 0.5
    d.rectangle((kx - 5, ky - 4, kx + 5, ky + 12), fill=(245, 245, 240))
    d.ellipse((kx - 7, ky - 14, kx + 7, ky - 2), fill=(245, 245, 240))
    d.line((kx, ky - 20, kx, ky - 12), fill=(245, 245, 240), width=3)
    # pawn
    d.ellipse((bx0 + (bx1 - bx0) * 0.25 - 5, by0 + (by1 - by0) * 0.66 - 8,
               bx0 + (bx1 - bx0) * 0.25 + 5, by0 + (by1 - by0) * 0.66 + 6), fill=(30, 30, 30))
    scene_label(d, x0, y0, "GAME 1", (240, 220, 180), (60, 54, 46))


def scene_helicopter(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(170, 188, 206))
    d.rectangle((x0, y1 - h * 0.22, x1, y1), fill=(150, 170, 130))
    # helicopter body
    d.ellipse((x0 + w * 0.28, y0 + h * 0.34, x0 + w * 0.66, y0 + h * 0.66), fill=(70, 90, 70))
    d.rectangle((x0 + w * 0.12, y0 + h * 0.44, x0 + w * 0.32, y0 + h * 0.52), fill=(70, 90, 70))
    d.line((x0 + w * 0.3, y0 + h * 0.34, x0 + w * 0.64, y0 + h * 0.66), fill=(50, 60, 50), width=2)
    # rotor
    d.line((x0 + w * 0.2, y0 + h * 0.22, x0 + w * 0.74, y0 + h * 0.22), fill=(40, 40, 40), width=3)
    d.line((x0 + w * 0.47, y0 + h * 0.22, x0 + w * 0.47, y0 + h * 0.34), fill=(40, 40, 40), width=3)
    # smoke
    for k, rad in enumerate((12, 8)):
        d.ellipse((x0 + w * 0.2 + k * 5, y1 - h * 0.28 - k * 5, x0 + w * 0.2 + k * 5 + rad, y1 - h * 0.28 - k * 5 + rad),
                  fill=(90, 88, 86))
    _mini_flag(d, x1 - 30, y0 + 6, 22, 14, [(220, 40, 40), (250, 250, 250)])
    scene_label(d, x0, y0, "TÜRKIYE", (40, 40, 60), (170, 188, 206))


def scene_huawei(d, r):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    d.rectangle(r, fill=(226, 226, 232))
    # phone
    px0, py0 = x0 + w * 0.28, y0 + h * 0.12
    px1, py1 = x0 + w * 0.5, y1 - h * 0.1
    d.rectangle((px0, py0, px1, py1), fill=(40, 44, 50), outline=(20, 20, 20))
    d.rectangle((px0 + 4, py0 + 5, px1 - 4, py1 - 5), fill=(70, 150, 200))
    # cell tower
    tx = x0 + w * 0.12
    d.line((tx - 10, y1 - h * 0.1, tx, y0 + h * 0.14), fill=(90, 90, 90), width=3)
    d.line((tx + 10, y1 - h * 0.1, tx, y0 + h * 0.14), fill=(90, 90, 90), width=3)
    d.line((tx - 6, y0 + h * 0.4, tx + 6, y0 + h * 0.4), fill=(90, 90, 90), width=2)
    # gavel
    gx = x0 + w * 0.72
    gy = y0 + h * 0.5
    d.rectangle((gx - 16, gy - 6, gx + 16, gy + 6), fill=(120, 80, 40))
    d.rectangle((gx - 4, gy + 4, gx + 4, gy + 26), fill=(120, 80, 40))
    _mini_flag(d, x1 - 30, y0 + 6, 22, 14, [(200, 40, 40), (250, 250, 250), (40, 60, 160)])
    scene_label(d, x0, y0, "GUILTY", (140, 30, 30), (226, 226, 232))


# ----------------------------------------------------------------------------
# content
# ----------------------------------------------------------------------------
EU, AS, AM, AF, ME, WO = "EU", "AS", "AM", "AF", "ME", "WO"

BIG = [
    dict(
        n=1, region=EU, tag="REPORTED", scene=scene_zaporizhzhia,
        head="Russian strike hits flats in Zaporizhzhia",
        sub="Two killed and 44 hurt as a bomb hits a five-storey block. (AP)",
    ),
    dict(
        n=2, region=AM, tag="REPORTED", scene=scene_markets,
        head="AI rally fades: Nvidia slides 7.7%",
        sub="Tech sell-off resumes; Anthropic drops below its $83 IPO price. (The Guardian)",
    ),
    dict(
        n=3, region=ME, tag="CLAIM", scene=scene_hormuz,
        head="Iran: mines hit three tankers in Hormuz",
        sub="Tehran says three vessels caught fire in the strait. (Al Jazeera)",
    ),
]

MEDIUM = [
    dict(n=4, region=AF, tag="REPORTED", scene=scene_afcon,
         loc="LAUSANNE",
         head="Senegal reinstated as Africa Cup champions",
         sub="CAS backs the 1-0 final win over Morocco. (AP)"),
    dict(n=5, region=ME, tag="REPORTED", scene=scene_gaza,
         loc="GAZA STRIP",
         head="Israel kills Hamas security chief in strike",
         sub="Naeem Abu Nahel dies in a Gaza air raid. (The Washington Post)"),
    dict(n=6, region=AS, tag="REPORTED", scene=scene_bangladesh,
         loc="DHAKA",
         head="Tear gas fired at garment protests",
         sub="Pay dispute halts work at 481 factories. (Business Standard)"),
    dict(n=7, region=AS, tag="REPORTED", scene=scene_hasina,
         loc="DHAKA, BANGLADESH",
         head="Hasina says she will return home",
         sub="Ex-PM plans to fly back on 16 December. (Reuters)"),
    dict(n=8, region=AM, tag="REPORTED", scene=scene_cartagena,
         loc="CARTAGENA",
         head="Hostages held in supermarket standoff",
         sub="Armed men flee botched robbery. (Al Jazeera)"),
    dict(n=9, region=WO, tag="REPORTED", scene=scene_femicide,
         loc="UNITED NATIONS",
         head="UN: a woman killed every 10 minutes",
         sub="5 an hour died at partners' or relatives' hands in 2025."),
    dict(n=10, region=EU, tag="REPORTED", scene=scene_ukheat,
         loc="UNITED KINGDOM",
         head="UK records its worst year for heat deaths",
         sub="5,258 heat-related deaths in 2026 set a record. (Reuters)"),
    dict(n=11, region=EU, tag="REPORTED", scene=scene_chess,
         loc="GENEVA",
         head="Chess title match opens with a draw",
         sub="Gukesh and Sindarov draw the 38-move opener. (Guardian)"),
    dict(n=12, region=ME, tag="REPORTED", scene=scene_helicopter,
         loc="ESKIŞEHIR, TÜRKIYE",
         head="Air force helicopter crash kills five",
         sub="Training flight comes down in central Türkiye. (AP)"),
    dict(n=13, region=AS, tag="REPORTED", scene=scene_huawei,
         loc="NEW YORK",
         head="Huawei guilty of stealing trade secrets",
         sub="Jury acquits it of racketeering in a US trial. (AP)"),
]

ALSO = [
    "Putin vows reply to oil strikes (RUSSIA)",
    "Ukraine hits Russian ships off Libya (LIBYA)",
    "Haftar visits Türkiye after ship attacks (LIBYA)",
    "S. Africa jails Zimbabwean over war (SA)",
    "China Southern to buy 50 Boeing jets (CHINA)",
    "Compass to quit London listing (UK)",
    "EU to cap Chinese hybrid-EV imports (EU)",
    "Leak: 300+ Russians killed in Mali (MALI)",
    "Cameroon separatist denies crimes (NORWAY)",
    "Landmine casualties hit 5-year high (GLOBAL)",
    "Rebels retreat in DR Congo (DR CONGO)",
    "China sentences official Ma to death (CHINA)",
    "Malaysia to return migrants to Myanmar",
    "Canada: 'We do not report to the US'",
    "Trump awards Giuliani Medal of Freedom (US)",
    "Democrat flips a Tennessee seat (US)",
    "Sooryavanshi smashes 204 off 53 (CRICKET)",
    "Sinner has knee surgery (TENNIS)",
    "Virginia enshrines vote, marriage rights (US)",
    "Gaza meningitis alert as cases rise (GAZA)",
]

EXCLUDED = [
    ("Huang reinstated as Nvidia CEO", "Mon 23 Nov"),
    ("US blacklists AI firm Megaspeed", "Mon 23 Nov"),
    ("Ukraine strikes Perm refinery", "Mon 23 Nov"),
    ("Car bomb, Villavicencio, Colombia", "Mon 23 Nov"),
    ("Mexico: 16 killed, 'El Chapo' held", "23 Nov"),
    ("GTA VI: $3.79bn first-day sales", "Fri 20 Nov"),
    ("Anthropic's record Nasdaq IPO", "Thu 19 Nov"),
    ("Court clears US Army Iowa blast", "Mon 23 Nov"),
    ("Trump urges faster executions", "Mon 23 Nov"),
    ("Sydney double-murder verdict", "Wed 25 Nov"),
    ("Saudi coalition bombs Hodeidah", "Wed 25 Nov"),
]

MARKETS = [
    ("Nvidia", "-7.7% to $152.35"),
    ("Nasdaq Composite", "-2.0%"),
    ("S&P 500", "-0.4% to 7,206"),
    ("Dow Jones", "+0.4% to 49,795"),
    ("Anthropic", "-9.75% to $79.08"),
    ("UK 2049 index-linked gilt", "record 2.5235% yield"),
    ("Gulf markets", "Saudi +0.4%, Dubai +0.8%"),
]

PINS = {
    1: (35.1, 47.8), 2: (-74.0, 40.7), 3: (56.5, 26.5),
    4: (6.6, 46.5), 5: (34.4, 31.5), 6: (90.4, 23.8), 7: (92.5, 25.5),
    8: (-75.5, 10.4), 9: (-73.9, 42.2), 10: (-0.1, 51.5), 11: (6.1, 44.0),
    12: (30.5, 39.8), 13: (-73.9, 38.9),
}


# ----------------------------------------------------------------------------
# layout
# ----------------------------------------------------------------------------
def draw_masthead(d):
    d.rectangle((MARGIN, 4, W - MARGIN, 8), fill=RULE)
    f_small = font(FONT_B, 13)
    text(d, (MARGIN + 2, 12), "THE WORLD PICTURE POST", f_small, INK)
    text(d, (W - MARGIN - 2, 12), "THE DAY IN ONE PICTURE", f_small, GREY, anchor="ra")
    f_date = font(FONT_SB, 50)
    text(d, (W / 2, 30), "TUESDAY 24 NOVEMBER 2026", f_date, INK, anchor="ma")
    d.rectangle((MARGIN, 88, W - MARGIN, 91), fill=RULE)


def draw_numbers(d):
    y = 96
    f = font(FONT_B, 13)
    counts = {}
    for s in BIG + MEDIUM:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    order = ["EU", "AS", "AM", "ME", "AF", "WO"]
    parts = [f"{REGION[c][1].upper()} {counts.get(c, 0)}" for c in order if counts.get(c)]
    line1 = "FEATURED BY REGION:  " + "  ·  ".join(parts) + "  ·  33 STORIES TOTAL"
    text(d, (MARGIN + 2, y), line1, f, INK)
    y += 17
    f2 = font(FONT_B, 12)
    text(d, (MARGIN + 2, y),
         "KEY NUMBERS:  Nvidia -7.7%  ·  Nasdaq -2%  ·  2 dead in Zaporizhzhia  ·  "
         "481 factories halted  ·  5,258 UK deaths  ·  a woman killed every 10 min",
         f2, (90, 30, 30))
    y += 16
    text(d, (MARGIN + 2, y),
         "HOW SURE ARE WE?  33 stories, each checked against a primary outlet for its EVENT date; "
         "11 other-day stories left out (see DATE CHECK).",
         font(FONT, 11), GREY)
    d.rectangle((MARGIN, y + 15, W - MARGIN, y + 16), fill=LIGHT)


def draw_big(d, y0, y1):
    gap = 8
    cw = (W - 2 * MARGIN - 2 * gap) / 3
    for i, s in enumerate(BIG):
        x0 = MARGIN + i * (cw + gap)
        x1 = x0 + cw
        box(d, (x0, y0, x1, y1), fill=PAPER, outline=RULE, width=2)
        ill_h = 150
        s["scene"](d, (x0 + 3, y0 + 3, x1 - 3, y0 + ill_h))
        # tag + region
        region_tag(d, (x0 + 5, y0 + ill_h + 6), s["region"])
        tag(d, (x1 - 64, y0 + ill_h + 6), s["tag"])
        # headline
        yy = block(d, (x0 + 7, y0 + ill_h + 22), s["head"], font(FONT_B, 20),
                   cw - 14, 22, INK, maxlines=3)
        block(d, (x0 + 7, yy + 2), s["sub"], font(FONT, 11), cw - 14, 12, GREY, maxlines=3)


def draw_medium(d, y0, y1):
    text(d, (MARGIN + 2, y0), f"TEN MORE OF THE DAY  ({len(MEDIUM)} stories, numbered 4-13)",
         font(FONT_B, 13), INK)
    gy = y0 + 18
    gap = 7
    cw = (W - 2 * MARGIN - 4 * gap) / 5
    rh = (y1 - gy - gap) / 2
    for idx, s in enumerate(MEDIUM):
        col = idx % 5
        row = idx // 5
        x0 = MARGIN + col * (cw + gap)
        y0c = gy + row * (rh + gap)
        x1 = x0 + cw
        y1c = y0c + rh
        box(d, (x0, y0c, x1, y1c), fill=PAPER, outline=RULE)
        ill_h = 54
        s["scene"](d, (x0 + 2, y0c + 2, x1 - 2, y0c + ill_h))
        # number + region + confidence
        text(d, (x0 + 4, y0c + ill_h + 3), f"{s['n']}.", font(FONT_B, 12), INK)
        region_tag(d, (x0 + 19, y0c + ill_h + 3), s["region"])
        tag(d, (x1 - 60, y0c + ill_h + 3), s["tag"])
        yy = block(d, (x0 + 4, y0c + ill_h + 19), s["head"], font(FONT_B, 12),
                   cw - 8, 14, INK, maxlines=2)
        block(d, (x0 + 4, yy + 2), s["loc"] + " — " + s["sub"], font(FONT, 9),
              cw - 8, 9, GREY, maxlines=2)


def draw_map(d, r, num_font):
    x0, y0, x1, y1 = r
    box(d, r, fill=(214, 226, 238), outline=RULE, width=2)
    text(d, (x0 + 6, y0 + 4), "WHERE IT HAPPENED", font(FONT_B, 12), (20, 40, 70))
    mx0, my0, mx1, my1 = x0 + 6, y0 + 20, x1 - 6, y1 - 6
    project = worldmap.make_projector(mx0, my0, mx1, my1)
    for poly in worldmap.CONTINENTS.values():
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(196, 208, 186), outline=(120, 140, 130))
    col, _ = REGION[EU]
    # pins that would sit on top of each other get a small nudge
    NUDGE = {11: (-15, 11), 13: (0, 13), 7: (13, -9)}
    for n, (lon, lat) in PINS.items():
        px, py = project(lon, lat)
        dx, dy = NUDGE.get(n, (0, 0))
        px, py = px + dx, py + dy
        reg = BIG[n - 1]["region"] if n <= 3 else MEDIUM[n - 4]["region"]
        c = REGION[reg][0]
        d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=c, outline=(255, 255, 255))
        text(d, (px, py - 1), str(n), num_font, (255, 255, 255), anchor="mm")


def draw_markets(d, r):
    x0, y0, x1, y1 = r
    box(d, r, fill=(30, 32, 40), outline=RULE, width=2)
    text(d, (x0 + 6, y0 + 4), "MARKETS & MONEY", font(FONT_B, 13), (250, 220, 130))
    y = y0 + 22
    for name, val in MARKETS:
        text(d, (x0 + 6, y), name, font(FONT_B, 11), (235, 235, 240))
        text(d, (x1 - 6, y), val, font(FONT, 11), (255, 160, 160), anchor="ra")
        y += 13
    text(d, (x0 + 6, y + 1), "All figures verified for Tue 24 Nov.", font(FONT, 8), (150, 150, 160))


def draw_also(d, r):
    x0, y0, x1, y1 = r
    box(d, r, fill=PAPER, outline=RULE, width=2)
    text(d, (x0 + 6, y0 + 4), "ALSO ON TUESDAY 24 NOVEMBER", font(FONT_B, 13), INK)
    yy0 = y0 + 22
    colw = (x1 - x0 - 18) / 2
    f = font(FONT, 9)
    half = (len(ALSO) + 1) // 2
    for i, item in enumerate(ALSO):
        c = 0 if i < half else 1
        row = i if c == 0 else i - half
        cx = x0 + 6 + c * (colw + 8)
        cy = yy0 + row * 13
        text(d, (cx, cy), f"{i + 1:>2}.", font(FONT_B, 9), (150, 60, 30))
        block(d, (cx + 18, cy), item, f, colw - 20, 10, INK, maxlines=1)


def draw_datecheck(d, r):
    x0, y0, x1, y1 = r
    box(d, r, fill=(240, 232, 214), outline=RULE, width=2)
    text(d, (x0 + 6, y0 + 4), "DATE CHECK", font(FONT_B, 13), (140, 40, 30))
    text(d, (x0 + 6, y0 + 21), "Every story here happened, or was first reported, on Tuesday 24 November 2026.",
         font(FONT, 10), INK)
    text(d, (x0 + 6, y0 + 33), "LEFT OUT AS OTHER DAYS' NEWS:", font(FONT_B, 10), (140, 40, 30))
    y = y0 + 46
    f = font(FONT, 9)
    colw = (x1 - x0 - 18) / 2
    half = (len(EXCLUDED) + 1) // 2
    for i, (label, date) in enumerate(EXCLUDED):
        c = 0 if i < half else 1
        row = i if c == 0 else i - half
        cx = x0 + 6 + c * (colw + 8)
        cy = y + row * 11
        block(d, (cx, cy), f"{label} — {date}", f, colw - 4, 10, INK, maxlines=1)


def draw_footer(d):
    text(d, (MARGIN + 2, H - 12),
         "Sources: AP · Reuters · AFP · The Guardian · BBC · Al Jazeera · The Washington Post · "
         "Gulf News · VnExpress · The Business Standard · The Daily Star · UKHSA · UN Women · CAS",
         font(FONT, 9), GREY)


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_numbers(d)
    draw_big(d, 154, 440)
    draw_medium(d, 448, 726)
    # bottom band
    draw_also(d, (MARGIN, 734, 486, 884))
    draw_datecheck(d, (MARGIN, 890, 486, 1002))
    draw_map(d, (494, 734, W - MARGIN, 864), font(FONT_B, 9))
    draw_markets(d, (494, 868, W - MARGIN, 1002))
    draw_footer(d)
    img.save(path, format="PNG")


if __name__ == "__main__":
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png"))

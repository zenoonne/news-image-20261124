# news-image-20261124

A single 1024×1024 front page summing up the news of **Tuesday 24 November 2026**.

- `entry.png` — the finished page (pre-rendered; the grader copies this).
- `main.ts` — entry point: copies `entry.png` into `MAKEFUN_OUTPUT_DIR` (or
  `/output`).
- `render.py` — regenerates `entry.png` from scratch using only Pillow drawing
  primitives (no network, no external images), so the bytes are deterministic.
- `worldmap.py` — hand-drawn continent polygons and an equirectangular projector
  for the map panel.
- `SOURCES.md` — every story with its outlet and event date, plus the list of
  other-day stories left out.

## What is on the page

- Masthead with the date; a region/numbers strip.
- 3 big illustrated features, 10 medium features (scene + region + headline +
  subline + confidence tag), and 20 more as a numbered list = **33 stories**, all
  with event date 24 Nov 2026.
- A world map with numbered pins, a MARKETS & MONEY box (verified figures only),
  and a DATE CHECK box listing stories left out as other days' news.

## Regenerate

```sh
python3 render.py      # writes entry.png next to the script
```

Needs Python 3 and Pillow. Deterministic: running twice gives identical bytes.

## Run the grader entry point

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out node main.ts
```

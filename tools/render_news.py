#!/usr/bin/env python3
"""Render a Konvex business-news card as feed (1080x1350) and story (1080x1920) JPEGs.

Usage: python3 tools/render_news.py news/2026-10-30/card.json
Writes feed.jpg and story.jpg next to the JSON file.

card.json keys:
  platform   SHOPIFY | META | WHATSAPP
  date       display date, e.g. "30 OCT 2026"
  headline   short headline, max ~6 words
  highlight  word(s) from headline shown in yellow (optional)
  changed    what changed, max ~30 words
  means      what it means for a store owner, max ~30 words
  action     one action to take, max ~14 words
  source     e.g. "Meta, WhatsApp Business Platform pricing"
"""
import html
import json
import pathlib
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = (ROOT / "fonts").as_uri()

CSS = """
@font-face{font-family:Bebas;src:url('%(f)s/bebas-neue-latin-400-normal.woff2')}
@font-face{font-family:Brico;font-weight:400;src:url('%(f)s/bricolage-grotesque-latin-400-normal.woff2')}
@font-face{font-family:Brico;font-weight:700;src:url('%(f)s/bricolage-grotesque-latin-700-normal.woff2')}
@font-face{font-family:Mono;font-weight:400;src:url('%(f)s/space-mono-latin-400-normal.woff2')}
@font-face{font-family:Mono;font-weight:700;src:url('%(f)s/space-mono-latin-700-normal.woff2')}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:%(h)dpx;background:#0A0A0A;color:#fff;font-family:Brico;
  padding:%(pad)dpx 72px;display:flex;flex-direction:column;gap:%(gap)dpx}
.top{display:flex;justify-content:space-between;align-items:center;font-family:Mono;
  font-size:26px;letter-spacing:.14em}
.tag{background:#FFE000;color:#0A0A0A;font-weight:700;padding:10px 20px;border:3px solid #FFE000}
.eyebrow{font-family:Mono;font-size:26px;letter-spacing:.14em;color:#FFE000}
h1{font-family:Bebas;font-weight:400;font-size:%(hs)dpx;line-height:.92;text-transform:uppercase}
h1 .hl{color:#FFE000}
.box{border:4px solid #fff;padding:30px 34px;box-shadow:10px 10px 0 #FFE000}
.lbl{font-family:Mono;font-size:22px;letter-spacing:.14em;margin-bottom:12px}
.box p,.ybox p{font-size:%(bs)dpx;line-height:1.3}
.ybox{background:#FFE000;color:#0A0A0A;padding:30px 34px}
.ybox .act{margin-top:16px;font-weight:700}
.spacer{flex:1}
.foot{display:flex;justify-content:space-between;align-items:flex-end;border-top:3px solid #FFE000;
  padding-top:24px}
.src{font-family:Mono;font-size:20px;color:#cfcfcf;max-width:620px;line-height:1.4}
.cta{font-family:Bebas;font-size:%(cs)dpx;color:#FFE000;line-height:1}
"""

LAYOUT = {
    "feed": dict(h=1350, pad=64, gap=34, hs=118, bs=31, cs=64),
    "story": dict(h=1920, pad=200, gap=48, hs=150, bs=36, cs=80),
}


def headline_html(head, hl):
    h = html.escape(head)
    if hl and hl in head:
        e = html.escape(hl)
        h = h.replace(e, f'<span class="hl">{e}</span>', 1)
    return h


def page(card, kind):
    L = LAYOUT[kind]
    css = CSS % dict(f=FONTS, **L)
    e = {k: html.escape(str(v)) for k, v in card.items()}
    story_cta = '<div class="eyebrow">FULL BREAKDOWN ON OUR FEED</div>' if kind == "story" else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="top"><span>KONVEX</span><span class="tag">{e['platform']} UPDATE</span></div>
<div class="eyebrow">BUSINESS NEWS · {e['date']}</div>
<h1>{headline_html(card['headline'], card.get('highlight'))}</h1>
<div class="box"><div class="lbl" style="color:#FFE000">WHAT CHANGED</div><p>{e['changed']}</p></div>
<div class="ybox"><div class="lbl">WHAT IT MEANS FOR YOUR STORE</div><p>{e['means']}</p>
<p class="act">→ {e['action']}</p></div>
<div class="spacer"></div>
{story_cta}
<div class="foot"><div class="src">SOURCE: {e['source']}</div><div class="cta">DM "AUDIT"</div></div>
</body></html>"""


def main(path):
    path = pathlib.Path(path).resolve()
    card = json.loads(path.read_text())
    out = path.parent
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for kind in ("feed", "story"):
            L = LAYOUT[kind]
            pg = b.new_page(viewport={"width": 1080, "height": L["h"]})
            tmp = out / f"_{kind}.html"
            tmp.write_text(page(card, kind))
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            overflow = pg.evaluate("document.body.scrollHeight > window.innerHeight")
            png = out / f"_{kind}.png"
            pg.screenshot(path=str(png))
            tmp.unlink()
            Image.open(png).convert("RGB").save(out / f"{kind}.jpg", "JPEG", quality=90)
            png.unlink()
            print(f"{kind}.jpg written{' (WARNING: text overflows, shorten copy)' if overflow else ''}")
        b.close()


if __name__ == "__main__":
    main(sys.argv[1])

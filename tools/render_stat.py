#!/usr/bin/env python3
"""Render a Konvex stat or quote card (1080x1350 JPEG).

Usage: python3 tools/render_stat.py posts/D04/stat.json
Writes 1.jpg next to the JSON file.

stat.json keys:
  eyebrow  short label, e.g. "WHO OWNS A PREMIUM PHONE?"
  big      the number, e.g. "9%"  (omit for a quote card)
  quote    shopper quote text    (use instead of big)
  line     supporting line, max ~25 words
  who      quote attribution, e.g. "Woman shopper, Gen X" (quote cards only)
  source   e.g. "dentsu x PhonePe, The Bharatiya Consumer (2024)"
  theme    "black" (default) | "yellow"
"""
import html
import json
import pathlib
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = (ROOT / "fonts").as_uri()


def page(c):
    yellow = c.get("theme") == "yellow"
    bg, ink, acc = ("#FFE000", "#0A0A0A", "#0A0A0A") if yellow else ("#0A0A0A", "#FFFFFF", "#FFE000")
    e = {k: html.escape(str(v)) for k, v in c.items()}
    if c.get("quote"):
        hero = (f'<div class="q">&ldquo;{e["quote"]}&rdquo;</div>'
                f'<div class="who">{e.get("who", "")}</div>')
    else:
        hero = f'<div class="big">{e["big"]}</div><div class="line">{e["line"]}</div>'
    extra = f'<div class="line">{e["line"]}</div>' if c.get("quote") and c.get("line") else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Bebas;src:url('{F}/bebas-neue-latin-400-normal.woff2')}}
@font-face{{font-family:Brico;font-weight:400;src:url('{F}/bricolage-grotesque-latin-400-normal.woff2')}}
@font-face{{font-family:Brico;font-weight:700;src:url('{F}/bricolage-grotesque-latin-700-normal.woff2')}}
@font-face{{font-family:Mono;src:url('{F}/space-mono-latin-400-normal.woff2')}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:{bg};color:{ink};font-family:Brico;padding:72px;
  display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;font-family:Mono;font-size:26px;letter-spacing:.14em}}
.rule{{height:8px;background:{acc};margin:28px 0 40px}}
.eb{{font-family:Mono;font-size:28px;letter-spacing:.14em;color:{acc}}}
.sp{{flex:1}}
.big{{font-family:Bebas;font-size:420px;line-height:.85;color:{acc}}}
.line{{font-size:46px;line-height:1.25;margin-top:28px;max-width:900px}}
.q{{font-size:62px;line-height:1.2;font-weight:700}}
.who{{font-family:Mono;font-size:26px;margin-top:30px;color:{acc}}}
.foot{{border-top:4px solid {acc};padding-top:24px;display:flex;justify-content:space-between;align-items:flex-end}}
.src{{font-family:Mono;font-size:22px;max-width:640px;line-height:1.4}}
.cta{{font-family:Bebas;font-size:64px;color:{acc};line-height:1}}
</style></head><body>
<div class="top"><span>KONVEX</span><span>KONVEXMARKETING.IN</span></div>
<div class="rule"></div>
<div class="eb">{e['eyebrow']}</div>
<div class="sp"></div>
{hero}{extra}
<div class="sp"></div>
<div class="foot"><div class="src">SOURCE: {e['source']}</div><div class="cta">DM "AUDIT"</div></div>
</body></html>"""


def main(p):
    p = pathlib.Path(p).resolve()
    c = json.loads(p.read_text())
    tmp = p.parent / "_card.html"
    tmp.write_text(page(c))
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto(tmp.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        over = pg.evaluate("document.body.scrollHeight > window.innerHeight")
        png = p.parent / "_card.png"
        pg.screenshot(path=str(png))
        b.close()
    Image.open(png).convert("RGB").save(p.parent / "1.jpg", "JPEG", quality=90)
    png.unlink()
    tmp.unlink()
    print("1.jpg written" + (" (WARNING: overflow, shorten copy)" if over else ""))


if __name__ == "__main__":
    main(sys.argv[1])

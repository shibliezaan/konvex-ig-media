#!/usr/bin/env python3
"""Render a single 1080x1350 Konvex carousel slide from an HTML body fragment.

Usage (as a module): render(body_html, bg, out_path, counter="03 / 07", dark=False)
Classes available in body_html: .eb (eyebrow), h1 (Bebas headline), .big (giant number),
p, .box (bordered), .ybox (yellow box), .src (source line), .hl (yellow text), .rule.
"""
import pathlib
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = (ROOT / "fonts").as_uri()


def html(body, bg, ink, acc, counter):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Bebas;src:url('{F}/bebas-neue-latin-400-normal.woff2')}}
@font-face{{font-family:Brico;font-weight:400;src:url('{F}/bricolage-grotesque-latin-400-normal.woff2')}}
@font-face{{font-family:Brico;font-weight:700;src:url('{F}/bricolage-grotesque-latin-700-normal.woff2')}}
@font-face{{font-family:Mono;src:url('{F}/space-mono-latin-400-normal.woff2')}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:{bg};color:{ink};font-family:Brico;padding:64px 64px 60px;
  display:flex;flex-direction:column;gap:30px}}
.top{{display:flex;justify-content:space-between;font-family:Mono;font-size:24px;letter-spacing:.12em}}
.eb{{font-family:Mono;font-size:24px;letter-spacing:.14em;color:{acc};text-transform:uppercase}}
h1{{font-family:Bebas;font-weight:400;font-size:120px;line-height:.92;text-transform:uppercase}}
h2{{font-family:Bebas;font-weight:400;font-size:84px;line-height:.95;text-transform:uppercase}}
.big{{font-family:Bebas;font-size:260px;line-height:.85}}
p{{font-size:38px;line-height:1.3}}
.hl{{color:#FFE000}}
.rule{{height:8px;background:{ink}}}
.box{{border:6px solid {ink};padding:28px 32px}}
.ybox{{background:#FFE000;color:#0A0A0A;border:6px solid #0A0A0A;padding:28px 32px}}
.sp{{flex:1}}
.src{{font-family:Mono;font-size:21px;line-height:1.4}}
.cols{{display:flex;gap:40px}} .cols>div{{flex:1}}
</style></head><body>
<div class="top"><span>KONVEX</span><span>{counter}</span></div>
{body}
</body></html>"""


def render(body, bg, out, counter, dark=False):
    ink = "#FFFFFF" if dark else "#0A0A0A"
    acc = "#FFE000" if dark else "#0A0A0A"
    out = pathlib.Path(out).resolve()
    tmp = out.with_suffix(".html")
    tmp.write_text(html(body, bg, ink, acc, counter))
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto(tmp.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        over = pg.evaluate("document.body.scrollHeight > window.innerHeight || document.body.scrollWidth > window.innerWidth")
        png = out.with_suffix(".png")
        pg.screenshot(path=str(png))
        b.close()
    Image.open(png).convert("RGB").save(out, "JPEG", quality=92)
    png.unlink()
    tmp.unlink()
    return over

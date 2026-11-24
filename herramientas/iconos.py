"""Genera los iconos de la app (Android y web) y las pantallas de arranque a partir del dibujo de las dos llaves."""
import asyncio, re
from pathlib import Path

# Chrome del sistema si existe; si no, el Chromium de Playwright («playwright install chromium»).
CHROME = {"executable_path": "/usr/bin/google-chrome", "args": ["--no-sandbox"]} if Path("/usr/bin/google-chrome").exists() else {}
from playwright.async_api import async_playwright

RAIZ = Path(__file__).resolve().parent.parent
src = (RAIZ / "doble-llave.html").read_text(encoding="utf-8")
llaves = re.search(r"const LLAVES_SVG = '(.*?)';", src).group(1).replace('stroke-width="2.2"', 'stroke-width="5.2"').replace('class="llaves"', '')
ORO, VELLUTO, NOTTE = "#D2B06A", "#3A1226", "#140610"
RES = RAIZ / "app-android/android/app/src/main/res"
WEB = RAIZ / "web"

def pagina(lado, fondo, ancho_llaves, forma="cuadrado"):
    radio = {"cuadrado": "0", "redondo": "50%", "suave": "18%"}[forma]
    fondo_css = "transparent" if fondo is None else f"radial-gradient(circle at 50% 38%, {VELLUTO} 0%, {NOTTE} 78%)"
    return f"""<html><body style="margin:0;background:transparent">
<div style="width:{lado}px;height:{lado}px;border-radius:{radio};background:{fondo_css};display:flex;align-items:center;justify-content:center;overflow:hidden">
<div style="width:{ancho_llaves}px;color:{ORO};display:flex">{llaves.replace('<svg ', '<svg style="width:100%;height:auto" ')}</div></div></body></html>"""

def splash(w, h):
    lado = min(w, h)
    return f"""<html><body style="margin:0;width:{w}px;height:{h}px;background:{NOTTE};display:flex;align-items:center;justify-content:center">
<div style="width:{int(lado*0.34)}px;color:{ORO};opacity:.9;display:flex">{llaves.replace('<svg ', '<svg style="width:100%;height:auto" ')}</div></body></html>"""

async def foto(page, html, w, h, ruta, transparente=False):
    await page.set_viewport_size({"width": w, "height": h})
    await page.set_content(html)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(ruta), omit_background=transparente, clip={"x": 0, "y": 0, "width": w, "height": h})

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(**CHROME)
        page = await b.new_page()
        dens = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
        for d, f in dens.items():
            n = int(48 * f); fg = int(108 * f)
            await foto(page, pagina(n, True, int(n * 0.74), "suave"), n, n, RES / f"mipmap-{d}/ic_launcher.png", True)
            await foto(page, pagina(n, True, int(n * 0.7), "redondo"), n, n, RES / f"mipmap-{d}/ic_launcher_round.png", True)
            # primer plano adaptable: las llaves dentro de la zona segura (66 de 108)
            await foto(page, pagina(fg, None, int(fg * 0.56)), fg, fg, RES / f"mipmap-{d}/ic_launcher_foreground.png", True)
        for carpeta in sorted(RES.glob("drawable*")):
            p = carpeta / "splash.png"
            if p.exists():
                from PIL import Image
                w, h = Image.open(p).size
                await foto(page, splash(w, h), w, h, p)
        for n in (180, 192, 512):
            await foto(page, pagina(n, True, int(n * 0.74), "cuadrado"), n, n, WEB / f"icono-{n}.png")
        await foto(page, pagina(512, True, int(512 * 0.56), "cuadrado"), 512, 512, WEB / "icono-adaptable-512.png")
        await b.close()
    (RES / "values/ic_launcher_background.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#2B0E1D</color>\n</resources>\n', encoding="utf-8")
    print("iconos y arranque generados")

asyncio.run(main())

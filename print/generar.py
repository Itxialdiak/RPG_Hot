#!/usr/bin/env python3
"""Genera los PDF para imprimir y jugar sin pantallas, uno por ambientación.

Lee los datos directamente de doble-llave.html (los mismos que usa la app),
maqueta cada página A4 en HTML y la convierte a PDF con Chrome.
"""
import asyncio, html, json, re, subprocess, sys
from pathlib import Path

# Chrome del sistema si existe; si no, el Chromium de Playwright («playwright install chromium»).
CHROME = {"executable_path": "/usr/bin/google-chrome", "args": ["--no-sandbox"]} if Path("/usr/bin/google-chrome").exists() else {}

RAIZ = Path(__file__).resolve().parent.parent
PRINT = RAIZ / "print"
SALIDA = RAIZ / "salida"
FUENTES = PRINT / "node_modules" / "@fontsource"


# ---------------------------------------------------------------- datos
def exportar_datos():
    src = (RAIZ / "doble-llave.html").read_text(encoding="utf-8")
    js = "\n".join(re.findall(r"<script>(.*?)</script>", src, re.S))
    corte = js.find("let S = nuevo();")
    (PRINT / "datos.js").write_text(js[:corte] + "\n;globalThis.__DATA = {MODOS, AMBIENTES, ETIQUETAS, SENALES, ANTES, ORACULO, ACELERANTES, FRENOS, CARTAS_PROPIAS, LLAVES_SVG, LUNA};\n", encoding="utf-8")
    subprocess.run(["node", str(PRINT / "exportar.js")], check=True, capture_output=True)
    return json.loads((PRINT / "datos.json").read_text(encoding="utf-8"))


def e(s):
    return html.escape(str(s), quote=True)


def con_pareja(s):
    """En papel no hay nombre de quien recibe: {R} pasa a ser «tu pareja»."""
    s = re.sub(r'(^|[.!?:]\s+|«)\{R\}', lambda m: m.group(1) + "Tu pareja", s)
    return s.replace("{R}", "tu pareja")


def minus(s):
    return s[:1].lower() + s[1:] if s else s


def lugar(escena):
    """«Sobre III: la Biblioteca Prohibida» -> «la Biblioteca Prohibida»."""
    return escena["sobre"].split(": ", 1)[-1]


def de(frase):
    return "del " + frase[3:] if frase.startswith("el ") else "de " + frase


def premio(x):
    F = x["fichas"]
    if F["inicial"] == 0:
        return f"quien haya cumplido el suyo recibe {F['una']} de su pareja."
    return f"quien haya cumplido el suyo gana {F['una']} más."


# ---------------------------------------------------------------- estilos
def fuente(familia, archivo, peso, estilo):
    return f'@font-face{{font-family:"{familia}";src:url("file://{FUENTES / archivo}") format("woff2");font-weight:{peso};font-style:{estilo};}}'


TEMAS = {
    "carnaval": {
        "display": '"Cormorant Garamond"',
        "fuentes": [fuente("Cormorant Garamond", f"cormorant-garamond/files/cormorant-garamond-latin-{p}-{s}.woff2", p, s)
                    for p in (500, 600) for s in ("normal", "italic")],
        "tit_peso": 600,
        "tinta": "#2B1B14", "gris": "#7A6A5E", "linea": "#D9CFC2", "oro": "#8C7142",
        "modo": {"prohibicion": "#7C1D2B", "encender": "#A33D1B", "explicito": "#9C2A5A", "rol": "#3F3A78"},
        "seda": "#3F6A6E", "brasa": "#A33D1B",
    },
    "fantasia": {
        "display": '"IM Fell English"',
        "fuentes": [fuente("IM Fell English", f"im-fell-english/files/im-fell-english-latin-400-{s}.woff2", 400, s)
                    for s in ("normal", "italic")],
        "tit_peso": 400,
        "tinta": "#1E2721", "gris": "#66705F", "linea": "#D3D6C6", "oro": "#6F7A55",
        "modo": {"prohibicion": "#4F3868", "encender": "#9E4320", "explicito": "#8E2A4E", "rol": "#2E5E73"},
        "seda": "#356457", "brasa": "#9E4320",
    },
    "cotidiana": {
        "display": '"Fraunces"',
        "fuentes": [fuente("Fraunces", f"fraunces/files/fraunces-latin-{p}-{s}.woff2", p, s)
                    for p in (400, 600) for s in ("normal", "italic")],
        "tit_peso": 400,
        "tinta": "#2A2118", "gris": "#76695B", "linea": "#DDD3C4", "oro": "#8A6A3E",
        "modo": {"prohibicion": "#86601A", "encender": "#A33D1B", "explicito": "#9A2D52", "rol": "#2F5873"},
        "seda": "#3E6577", "brasa": "#A33D1B",
    },
}

# Lo que cambia de una ambientación a otra en las páginas comunes.
LLAVE_PATHS = ('<path d="M13 12a8 8 0 1 0 0 16a8 8 0 0 0 0-16Zm0 4.8a3.2 3.2 0 1 1 0 6.4a3.2 3.2 0 0 1 0-6.4Z" fill-rule="evenodd"/>'
               '<path d="M20.5 18.3H36v3.4h-3v5.3h-3.2v-5.3h-2.6v3.8H24v-3.8h-3.5Z"/>')
PAPEL = {
    "_": {"titulo": "Máscaras y nombres", "una": "una máscara", "h2": "Las máscaras", "elige": "máscara",
          "nota": "Si no tenéis máscaras de verdad, cualquier antifaz sirve: lo que cuenta es quién decides ser esta noche.",
          "durante": "Os llamáis por el nombre de personaje hasta la última escena, que es cuando caen las máscaras. Salir del personaje está permitido siempre.",
          "abre": "Quien esperaba dentro", "monedas": "monedas de chocolate",
          "llega": "Decidid quién espera dentro y quién llega de fuera. Preparaos por separado, como para una cita con alguien a quien no conocéis. Quien llega, llama a la puerta; quien espera, abre la primera carta."},
    "cotidiana": {"titulo": "Papeles y nombres", "una": "un papel (quién es en este edificio)", "h2": "Los papeles", "elige": "papel",
          "nota": "Aquí no hacen falta disfraces: ropa de estar por casa y un poco de imaginación. Lo que cuenta es quién decides ser esta tarde.",
          "durante": "Os llamáis por el nombre de personaje hasta la última escena, cuando por fin os miráis con la luz encendida. Salir del personaje está permitido siempre.",
          "abre": "Quien vive aquí", "monedas": "monedas ni garbanzos a mano",
          "llega": "Decidid quién vive aquí y quién llama a la puerta. Quien llama sale al rellano sin llaves y toca el timbre; quien vive aquí abre y lee la primera carta con la puerta todavía abierta."},
}
# La puerta de enfrente dura una tarde: lo común dice «noche» y se ajusta al final (igual que en la app).
A_TARDE = [(re.compile(r"Buenas noches"), "Hasta otra tarde"), (re.compile(r"hasta el amanecer"), "hasta mañana"),
           (re.compile(r"\b(Esta|esta|La|la|Una|una|Otra|otra|buena) noche\b"), r"\1 tarde")]


def a_tarde(doc):
    for r, x in A_TARDE:
        doc = r.sub(x, doc)
    return doc


def css(t):
    return "\n".join(t["fuentes"]) + f"""
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{ font-family: "TeX Gyre Pagella", "Palatino Linotype", Palatino, serif; color: {t['tinta']};
  font-size: 10.4pt; line-height: 1.45; -webkit-print-color-adjust: exact; print-color-adjust: exact;
  font-variant-numeric: oldstyle-nums; hyphens: manual; }}
.hoja {{ width: 210mm; height: 297mm; position: relative; overflow: hidden; break-after: page; }}
.hoja:last-child {{ break-after: auto; }}
.cuerpo {{ position: absolute; left: 31mm; right: 31mm; top: 23mm; bottom: 19mm; overflow: hidden; }}
.cabeza {{ position: absolute; top: 11mm; left: 31mm; right: 31mm; font-style: italic; font-size: 8.6pt; color: var(--acento); }}
.pie {{ position: absolute; bottom: 9mm; left: 0; right: 0; text-align: center; font-size: 8.6pt; color: {t['gris']}; }}
.display, h1, h2, h3 {{ font-family: {t['display']}; font-weight: {t['tit_peso']}; }}
h1 {{ font-size: 30pt; line-height: 1.02; font-style: italic; margin: 0 0 3mm; color: var(--acento); }}
h2 {{ font-size: 17pt; line-height: 1.1; font-style: italic; margin: 5.5mm 0 1.8mm; color: var(--acento); }}
h3 {{ font-size: 13pt; line-height: 1.15; font-style: italic; margin: 4mm 0 1.2mm; color: var(--acento); }}
p {{ margin: 0 0 2.2mm; }}
.lead {{ font-size: 12pt; line-height: 1.42; font-style: italic; }}
.sub {{ color: {t['gris']}; }}
.peq {{ font-size: 9pt; line-height: 1.4; }}
ul.lista, ol.pasos {{ margin: 0 0 2.4mm; padding-left: 5.5mm; }}
ul.lista li, ol.pasos li {{ margin: 0 0 1.3mm; padding-left: 0.6mm; }}
ol.pasos li::marker {{ font-family: {t['display']}; font-style: italic; color: var(--acento); font-size: 11.5pt; }}
ul.lista li::marker {{ color: var(--acento); }}
.casillas {{ list-style: none; padding: 0; margin: 0 0 2.4mm; }}
.casillas li {{ position: relative; padding-left: 6.5mm; margin: 0 0 1.4mm; }}
.casillas li::before {{ content: ""; position: absolute; left: 0; top: 1.1mm; width: 3.2mm; height: 3.2mm; border: 0.3mm solid {t['oro']}; border-radius: 0.6mm; }}
.dos-col {{ columns: 2; column-gap: 8mm; }}
.dos-col li {{ break-inside: avoid; }}
.recuadro {{ border-top: 0.35mm solid var(--acento); border-bottom: 0.35mm solid var(--acento); padding: 2.6mm 0 1.4mm; margin: 3.5mm 0; }}
.recuadro .rotulo {{ font-family: {t['display']}; font-style: italic; font-size: 12pt; color: var(--acento); margin-bottom: 1mm; }}
dl.def {{ margin: 0; display: grid; grid-template-columns: 30mm 1fr; column-gap: 4mm; row-gap: 1.2mm; }}
dl.def dt {{ font-style: italic; color: var(--acento); }}
dl.def dd {{ margin: 0; }}
table.tabla {{ width: 100%; border-collapse: collapse; font-size: 9.2pt; line-height: 1.35; }}
table.tabla td {{ padding: 1.4mm 2mm 1.4mm 0; border-bottom: 0.2mm solid {t['linea']}; vertical-align: top; }}
table.tabla td:first-child {{ font-style: italic; color: var(--acento); width: 37mm; }}
.indice td:last-child {{ text-align: right; white-space: nowrap; color: {t['gris']}; }}

/* portada */
.portada {{ text-align: center; }}
.portada .llaves {{ width: 66mm; color: var(--acento); margin: 46mm auto 7mm; display: block; }}
.portada .marca {{ font-family: {t['display']}; font-size: 15pt; letter-spacing: 0.06em; color: {t['oro']}; margin-bottom: 9mm; }}
.portada h1 {{ font-size: 44pt; margin-bottom: 4mm; }}
.portada .lugar {{ font-style: italic; font-size: 13pt; color: {t['gris']}; margin-bottom: 4mm; }}
.portada .sin-pantallas {{ font-size: 10.5pt; color: {t['gris']}; margin-bottom: 30mm; }}
.portada .aventuras {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10mm; text-align: left; margin: 0 6mm; }}
.portada .aventura {{ border-top: 0.5mm solid var(--acento); padding-top: 3mm; }}
.portada .aventura b {{ display: block; font-family: {t['display']}; font-style: italic; font-weight: {t['tit_peso']}; font-size: 15pt; line-height: 1.12; margin-bottom: 1.6mm; }}
.portada.cuatro .llaves {{ width: 52mm; margin: 24mm auto 5mm; }}
.portada.cuatro .marca {{ margin-bottom: 6mm; }}
.portada.cuatro h1 {{ font-size: 40pt; margin-bottom: 3mm; }}
.portada.cuatro .sin-pantallas {{ margin-bottom: 13mm; }}
.portada.cuatro .aventuras {{ gap: 7mm 10mm; font-size: 9.6pt; line-height: 1.4; }}
.portada.cuatro .aventura b {{ font-size: 14pt; }}
.portada .nota-adulta {{ position: absolute; left: 31mm; right: 31mm; bottom: 22mm; font-size: 9pt; color: {t['gris']}; font-style: italic; }}

/* cartas de escena (A4, para leer en voz alta y doblar en tres) */
.carta-hoja .cuerpo {{ top: 20mm; bottom: 16mm; left: 28mm; right: 28mm; }}
.carta-hoja .sobre {{ font-style: italic; color: var(--acento); font-size: 10pt; margin-bottom: 1mm; }}
.carta-hoja .antes {{ font-size: 9pt; color: {t['gris']}; font-style: italic; margin-bottom: 6mm; }}
.carta-hoja .texto p {{ font-size: 11.6pt; line-height: 1.52; margin: 0 0 3mm; }}
.carta-hoja .texto p.fecha {{ text-align: right; font-style: italic; }}
.carta-hoja .firma {{ text-align: right; font-family: {t['display']}; font-style: italic; font-size: 14pt; margin: 3mm 0 0; }}
.carta-hoja .sello {{ width: 15mm; height: 15mm; margin: 1mm 0 0 auto; display: block; }}
.pliegue {{ position: absolute; width: 5mm; border-top: 0.25mm solid {t['linea']}; }}

/* naipes */
.rejilla {{ position: absolute; left: 10.5mm; top: 16.5mm; width: 189mm; height: 264mm; display: grid;
  grid-template-columns: repeat(3, 63mm); grid-template-rows: repeat(3, 88mm); }}
.naipe {{ position: relative; width: 63mm; height: 88mm; box-shadow: inset 0 0 0 0.15mm #C8C1B8; }}
.marco {{ position: absolute; inset: 3.3mm; border: 0.3mm solid var(--acento-suave); border-radius: 2.2mm;
  padding: 3mm 3.4mm 2.4mm; display: flex; flex-direction: column; overflow: hidden; }}
.n-cab {{ display: flex; justify-content: space-between; align-items: baseline; gap: 2mm; font-size: 7pt; line-height: 1.2; font-style: italic; color: var(--acento); }}
.n-cab .sala {{ overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
.pips {{ font-style: normal; letter-spacing: 0.4mm; font-size: 7.5pt; white-space: nowrap; }}
.pips .off {{ opacity: 0.25; }}
.temp {{ font-style: normal; font-size: 7pt; border: 0.28mm solid currentColor; border-radius: 3mm; padding: 0.1mm 1.7mm; white-space: nowrap; }}
.temp.seda {{ color: {t['seda']}; }}
.temp.brasa {{ color: {t['brasa']}; }}
.n-tit {{ font-family: {t['display']}; font-style: italic; font-weight: {t['tit_peso']}; font-size: 14.2pt; line-height: 1.06; margin: 2.1mm 0 1.9mm; color: var(--acento); }}
.n-txt {{ font-size: 9.15pt; line-height: 1.34; flex: 1; overflow: hidden; }}
.n-txt p {{ margin: 0 0 1.4mm; }}
.n-pie {{ display: flex; justify-content: space-between; gap: 2mm; border-top: 0.2mm solid {t['linea']}; padding-top: 1.1mm; font-size: 6.6pt; line-height: 1.25; font-style: italic; color: {t['gris']}; }}
.n-pie .tags {{ color: var(--acento); }}
.renglones {{ flex: 1; background: repeating-linear-gradient(180deg, transparent 0 5.6mm, {t['linea']} 5.6mm 5.85mm); margin-top: 1mm; }}
.campo {{ font-size: 7.6pt; font-style: italic; color: {t['gris']}; margin: 1mm 0 0; }}
.centro {{ text-align: center; }}
.grande {{ font-family: {t['display']}; font-size: 40pt; line-height: 1; margin: 7mm 0 3mm; color: var(--acento); }}
.llave-dib {{ width: 30mm; margin: 6mm auto 3mm; display: block; color: var(--acento); }}
.marca-corte {{ position: absolute; background: #9A938A; }}

/* fichas */
.fichas {{ position: absolute; left: 16mm; right: 16mm; top: 30mm; display: grid; grid-template-columns: repeat(6, 26mm); gap: 4mm 4.8mm; justify-content: center; }}
.ficha {{ width: 26mm; height: 26mm; border-radius: 50%; border: 0.35mm solid var(--acento); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
.ficha b {{ font-family: {t['display']}; font-style: italic; font-weight: {t['tit_peso']}; font-size: 15pt; line-height: 1; color: var(--acento); }}
.ficha span {{ font-size: 6.4pt; font-style: italic; color: {t['gris']}; margin-top: 0.8mm; max-width: 20mm; line-height: 1.15; }}

/* rótulos e invitaciones */
.rotulos {{ position: absolute; left: 17mm; right: 17mm; top: 30mm; display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }}
.rotulo-sobre {{ border: 0.3mm dashed #B5ADA2; padding: 3.5mm 4mm; height: 36mm; overflow: hidden; }}
.rotulo-sobre .display {{ font-style: italic; font-size: 13.5pt; line-height: 1.1; color: var(--acento); }}
.rotulo-sobre .modo {{ font-size: 7.6pt; font-style: italic; color: {t['gris']}; }}
.rotulo-sobre p {{ font-size: 8.6pt; line-height: 1.35; margin: 1.5mm 0 0; }}
.mitad {{ position: absolute; left: 0; right: 0; height: 148.5mm; }}
.mitad.arriba {{ top: 0; }} .mitad.abajo {{ top: 148.5mm; }}
.mitad .dentro {{ position: absolute; left: 24mm; right: 24mm; top: 13mm; bottom: 10mm; overflow: hidden; }}
.corte-medio {{ position: absolute; left: 10mm; right: 10mm; top: 148.5mm; border-top: 0.3mm dashed #B5ADA2; }}
.linea-rellenar {{ display: inline-block; min-width: 52mm; border-bottom: 0.25mm solid {t['gris']}; height: 4.2mm; vertical-align: baseline; }}

/* dorsos */
.dorso {{ position: relative; width: 63mm; height: 88mm; overflow: hidden; }}
.dorso .fondo {{ position: absolute; inset: 3.3mm; border-radius: 2.2mm; border: 0.3mm solid var(--acento);
  background:
    repeating-linear-gradient(45deg, var(--rombo) 0 0.25mm, transparent 0.25mm 4.2mm),
    repeating-linear-gradient(-45deg, var(--rombo) 0 0.25mm, transparent 0.25mm 4.2mm); }}
.dorso .medalla {{ position: absolute; left: 50%; top: 50%; width: 31mm; height: 31mm; margin: -15.5mm 0 0 -15.5mm; border-radius: 50%;
  background: #fff; border: 0.35mm solid var(--acento); display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.dorso .medalla svg {{ width: 21mm; color: var(--acento); }}
.dorso .medalla span {{ font-family: {t['display']}; font-style: italic; font-size: 8.5pt; color: var(--acento); margin-top: 0.6mm; }}
"""


# ---------------------------------------------------------------- utilidades de página
class Libro:
    def __init__(self, tema):
        self.tema = tema
        self.paginas = []        # (html, acento)
        self.marcas = {}         # nombre -> número de página

    def marca(self, nombre):
        self.marcas[nombre] = len(self.paginas) + 1

    def hoja(self, contenido, acento, clase="", cabeza="", pie=True):
        n = len(self.paginas) + 1
        h = (f'<section class="hoja {clase}" style="--acento:{acento};--acento-suave:{acento}55;--rombo:{acento}22">'
             + (f'<div class="cabeza">{e(cabeza)}</div>' if cabeza else "")
             + contenido
             + (f'<div class="pie">{n}</div>' if pie else "")
             + "</section>")
        self.paginas.append(h)
        return n


def marcas_de_corte():
    xs = [10.5, 73.5, 136.5, 199.5]
    ys = [16.5, 104.5, 192.5, 280.5]
    out = []
    for x in xs:
        out.append(f'<div class="marca-corte" style="left:{x - 0.1}mm;top:5mm;width:0.2mm;height:8mm"></div>')
        out.append(f'<div class="marca-corte" style="left:{x - 0.1}mm;bottom:5mm;width:0.2mm;height:8mm"></div>')
    for y in ys:
        out.append(f'<div class="marca-corte" style="top:{y - 0.1}mm;left:1mm;height:0.2mm;width:7mm"></div>')
        out.append(f'<div class="marca-corte" style="top:{y - 0.1}mm;right:1mm;height:0.2mm;width:7mm"></div>')
    return "".join(out)


def hojas_de_naipes(libro, naipes, acento, cabeza):
    paginas = []
    for i in range(0, len(naipes), 9):
        grupo = naipes[i:i + 9]
        grupo += ['<div class="naipe"></div>'] * (9 - len(grupo))
        paginas.append(libro.hoja('<div class="rejilla">' + "".join(grupo) + "</div>" + marcas_de_corte(), acento, cabeza="", pie=False))
    return paginas


def naipe(cab_izq, cab_der, titulo, cuerpo, pie_izq="", pie_der="", extra_clase=""):
    return (f'<div class="naipe {extra_clase}"><div class="marco">'
            f'<div class="n-cab"><span class="sala">{cab_izq}</span>{cab_der}</div>'
            + (f'<div class="n-tit">{titulo}</div>' if titulo else "")
            + f'<div class="n-txt">{cuerpo}</div>'
            + (f'<div class="n-pie"><span class="tags">{pie_izq}</span><span>{pie_der}</span></div>' if (pie_izq or pie_der) else "")
            + "</div></div>")


def pips(n):
    return '<span class="pips">' + "●" * n + '<span class="off">' + "●" * (4 - n) + "</span></span>"


def temp(t):
    return f'<span class="temp {t}">{"Seda" if t == "seda" else "Brasa"}</span>'


# ---------------------------------------------------------------- textos para papel
SENALES_PAPEL = [
    ("«Ámbar»", "Más despacio o menos intensidad. Se ajusta y se sigue."),
    ("«Rojo»", "Se para todo, fuera de personaje y sin reproches. Después, lo que haga falta: hablar, un abrazo o dejarlo ahí."),
    ("Tres golpecitos", "Igual que «rojo», para cuando no se puede hablar."),
    ("Cambiar carta", "Cualquier persona cambia cualquier carta sin explicar por qué: va debajo del mazo y se roba otra."),
    ("Salir del personaje", "Permitido siempre."),
    ("Con las muñecas atadas", "«Rojo» se puede decir siempre, aunque una carta pida silencio, y el nudo se suelta al momento, sin preguntas."),
    ("Pausa", "Agua, un abrazo, respirad. La partida espera y nadie pierde nada."),
]


def escenas_de(x):
    guiada = next(s for s in x["escenas"] if s["tipo"] == "guiada")
    mazos = [s for s in x["escenas"] if s["tipo"] == "mazo"]
    final = next(s for s in x["escenas"] if s["tipo"] == "final")
    oraculo = next(s for s in x["escenas"] if s.get("oraculo"))
    return guiada, mazos, final, oraculo


def tabla_escenas(x):
    filas = "".join(f'<tr><td>{e(s["nombre"])}</td><td>{e(s["luz"])}. {e(s["musica"])}{", unos " + str(s["min"]) + " minutos" if s.get("min") else ""}.</td></tr>' for s in x["escenas"])
    return f'<table class="tabla">{filas}</table>'


def material_html(x):
    return '<ul class="casillas">' + "".join(f"<li>{e(m)}</li>" for m in x["material"]) + "</ul>"


# ---------------------------------------------------------------- construcción
MODOS_PDF = ["prohibicion", "encender", "explicito", "rol"]
CUANTAS = {1: "una", 2: "dos", 3: "tres", 4: "cuatro"}


def construir(D, amb):
    t = TEMAS[amb]
    A = D["AMBIENTES"][amb]
    M = D["MODOS"]
    modos = [m for m in MODOS_PDF if m in A["modos"]]
    X = {m: A["modos"][m] for m in modos}
    ac = {m: t["modo"][m] for m in modos}
    acN = t["oro"]
    O = A["oraculo"]
    libro = Libro(t)
    llaves = D["LLAVES_SVG"]
    sello_txt = A["sello"]
    etq = {x["id"]: x for x in D["ETIQUETAS"]}
    T = PAPEL.get(amb, PAPEL["_"])
    n_av = CUANTAS[len(modos)]
    para_todas = f"Para las {n_av} aventuras"
    hay_extra = [m for m in modos if any(c.get("extra") for s in X[m]["escenas"] for c in s.get("cartas", []))]

    def nom(m):
        return M[m]["nombre"]

    def subt(m):
        s = X[m]["titulo"].split(": ", 1)[-1]
        return s[:1].upper() + s[1:]

    def fichas_txt(F):
        return "el oro de hada" if F["nombre"] == "Oro de hada" else minus(F["nombre"])

    def con_giros(x):
        return any(s.get("giros") for s in x["escenas"])

    # Las etiquetas raras (juguetes, tocarse, al borde) solo salen en los NO si algo de esta ambientación las usa.
    usadas = set()
    for m in modos:
        for s in X[m]["escenas"]:
            for c in s.get("cartas", []) + s.get("giros", []):
                usadas.update(c.get("tags", []))
        for sec in X[m]["secretos"]:
            usadas.update(sec.get("tags", []))
    for d in D["ORACULO"] + D["ACELERANTES"]:
        usadas.update(d.get("tags", []))

    def sello_svg(color):
        if sello_txt == "luna":
            dentro = '<path d="M27 15A12 12 0 1 0 35 36A11 11 0 0 1 27 15Z" fill="#fff" opacity=".92"/>'
        elif sello_txt == "llave":
            dentro = f'<g transform="translate(9 9) scale(.8)" fill="#fff" opacity=".92">{LLAVE_PATHS}</g>'
        else:
            dentro = f'<text x="25" y="33" text-anchor="middle" font-family={t["display"]!r} font-style="italic" font-size="23" fill="#fff" opacity=".92">{e(sello_txt)}</text>'
        return (f'<svg class="sello" viewBox="0 0 50 50" aria-hidden="true"><path d="M25 2c4 0 5 3 8 4s7-1 9 2 0 6 2 9 5 4 4 8-4 5-4 8 2 7-1 9-6 0-9 2-4 5-8 5-5-3-8-4-7 1-9-2 0-6-2-9-5-4-4-8 4-5 4-8-2-7 1-9 6 0 9-2 4-5 8-5z" fill="{color}"/>'
                f'<circle cx="25" cy="25" r="15" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1"/>{dentro}</svg>')

    # ---------- 1. portada
    def portada():
        av = "".join(f'<div class="aventura" style="--acento:{ac[m]}"><b style="color:{ac[m]}">{e(nom(m))}</b>{e(subt(m))}. {e(M[m]["corto"])}</div>' for m in modos)
        return libro.hoja(
            f'<div class="portada{" cuatro" if len(modos) > 2 else ""}">{llaves}<div class="marca">Doble Llave</div>'
            f'<h1>{e(A["nombre"])}</h1><div class="lugar">{e(A["lugar"])}</div><div class="sin-pantallas">{e(n_av.capitalize())} aventuras para imprimir y jugar sin pantallas</div>'
            f'<div class="aventuras">{av}</div>'
            '<p class="nota-adulta">Un juego para dos personas adultas que quieren jugar: todo se puede cambiar, parar o dejar para otra noche.</p></div>',
            acN, pie=False)

    # ---------- 2. antes de imprimir (se rellena al final con los números de página)
    def como_usar(p):
        filas = [(para_todas, f'{p["comun"][0]}–{p["comun"][1]} y {p["final_comun"][0]}–{p["final_comun"][1]}')]
        filas += [(nom(m), f'{p[m][0]}–{p[m][1]}') for m in modos]
        papeles = ", los papeles secretos" if "rol" in modos else ""
        return libro.hoja(
            '<div class="cuerpo">'
            '<h1>Antes de imprimir</h1>'
            f'<p class="lead">Este cuaderno trae las {n_av} aventuras {e(de(minus(A["nombre"])))}, completas y para jugar sin pantallas: las cartas que se leen en voz alta, los mazos, los giros de la historia{papeles}, los Secretos, {e(O["corto"])}, las fichas y las hojas privadas.</p>'
            '<h2>Qué hay dentro</h2>'
            '<table class="tabla indice">' + "".join(f"<tr><td>{e(a)}</td><td></td><td>páginas {b}</td></tr>" for a, b in filas) + "</table>"
            '<h2>Qué imprimir</h2>'
            f'<p>No hace falta imprimirlo todo: las páginas comunes ({p["comun"][0]}–{p["comun"][1]}), las de la aventura que vayáis a jugar y, de las del final, solo lo que pida su lista «Para imprimir y recortar». Los dorsos de las cartas, en la página {p["final_comun"][1]}, son opcionales.</p>'
            '<h2>Cómo imprimir</h2>'
            '<ul class="lista">'
            '<li>En A4 y a tamaño real: en el cuadro de impresión, «100 %» o «tamaño real», nunca «ajustar a la página». Las cartas miden 63 × 88 mm, como una baraja de póker.</li>'
            '<li>Las hojas de cartas, mejor en papel grueso o cartulina fina (160 a 250 g): así no se transparenta el texto al robar. Si solo tenéis papel normal, meted cada carta en una funda de baraja.</li>'
            '<li>Recortad por las líneas grises; las marcas de los bordes sirven para una guillotina.</li>'
            '<li>Dorsos: si vuestra impresora imprime a doble cara, imprimid la última página por detrás de cada hoja de cartas, girando por el borde largo. El dibujo es simétrico, así que un par de milímetros de desvío no se notan.</li>'
            '<li>Las cartas que se leen en voz alta, en papel normal. Se doblan en tres y van cada una en su sobre, con su rótulo.</li>'
            '<li>Funciona en blanco y negro: la temperatura de cada carta, Seda o Brasa, va escrita, y el nivel se ve en los puntos de arriba.</li></ul>'
            '<h2>Además, tened a mano</h2>'
            '<p>Tijeras, seis sobres (o folios doblados) para las cartas que se leen en voz alta y dos sobres pequeños para las cartas que escribe cada persona, un bolígrafo, música para cada escena y lo que pide la lista de cada aventura.</p>'
            '</div>', acN)

    # ---------- 3-5. común
    def comun_siempre():
        filas = "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in SENALES_PAPEL)
        noes = "".join(f'<li><b>{e(x["n"])}.</b> {e(x["d"])}.</li>' for x in D["ETIQUETAS"]
                       if not x.get("escapada") and (not x.get("raro") or x["id"] in usadas))
        return libro.hoja(
            '<div class="cuerpo">'
            '<h1>Lo que vale siempre</h1>'
            f'<p class="lead">Las mismas reglas para las {n_av} aventuras, de la primera carta hasta el amanecer.</p>'
            f'<h2>Las señales</h2><dl class="def">{filas}</dl>'
            '<h2>Los NO</h2>'
            '<p>Antes de empezar, leed juntos esta lista. Basta con que una persona marque algo: un NO no se explica ni se discute, y vale hasta el amanecer.</p>'
            f'<ul class="casillas dos-col peq">{noes}</ul>'
            '<p class="peq">Quitad del juego las cartas que lleven algo marcado. Cada carta lo indica en su franja de abajo: miradla sin leer el resto, que la sorpresa también cuenta. Lo mismo con los giros, los Secretos, los deseos y las cartas de lo que enciende.</p>'
            '<p class="peq"><i>Fijo en todas las partidas:</i> nada de fotos ni vídeo.</p>'
            '</div>', acN, cabeza=para_todas)

    def comun_antes():
        antes = "".join(f"<li>{e(x)}</li>" for x in (A.get("antes") or D["ANTES"]))
        return libro.hoja(
            '<div class="cuerpo">'
            '<h1>Antes de la noche</h1>'
            f'<ul class="casillas">{antes}</ul>'
            '<h2>La invitación</h2>'
            f'<p>Al final del cuaderno hay {n_av} invitaciones, una por aventura. Rellenad la vuestra y entregadla con tiempo: la espera también enciende.</p>'
            '<h2>Las cartas que se leen en voz alta</h2>'
            '<p>Cada escena empieza con una carta de quien os invita. Recortad el rótulo de cada una, doblad la carta en tres por las marcas del borde y guardadla en su sobre. Se abren en orden, solo cuando la Puerta lo permita.</p>'
            '<h2>La música</h2>'
            '<p>Cada escena dura lo que su música, unos veinte minutos. Preparad antes una lista para cada una: la tabla de cada aventura dice qué tipo de música va bien. Cuando acabe, se va a la Puerta.</p>'
            '<h2>Quién llega</h2>'
            f'<p>{e(T["llega"])}</p>'
            '<h2>Las dos llaves</h2>'
            '<p>Cada persona tiene una. Entre escena y escena, la Puerta: cada cual esconde su llave a la espalda y saca el puño, con la llave si quiere seguir o vacío si no. A la de tres, abrís las manos a la vez. Con dos llaves se sigue; con una, la noche termina con un final suave, y no es un fracaso. Nadie pregunta por qué.</p>'
            '</div>', acN, cabeza=para_todas)

    def comun_mascaras():
        masc = "".join(f'<tr><td>{e(m["n"])}</td><td>{e(m["quien"])}. {e(m["como"])}.</td></tr>' for m in A["mascaras"])
        return libro.hoja(
            '<div class="cuerpo">'
            f'<h1>{e(T["titulo"])}</h1>'
            f'<p class="lead">En la primera escena cada persona elige, sin que la otra lo vea, {e(T["una"])}, un nombre que no sea el suyo y un Secreto.</p>'
            f'<h2>{e(T["h2"])}</h2><table class="tabla">{masc}</table>'
            f'<p class="peq sub" style="margin-top:2mm">{e(T["nota"])}</p>'
            f'<h2>Los nombres</h2><p><i>Nombres:</i> {e(", ".join(A["nombres"]))}.</p><p><i>{"Apodos" if amb == "fantasia" else "Apellidos"}:</i> {e(", ".join(A["apellidos"]))}.</p>'
            '<p class="peq">Para elegir al azar: cerrad los ojos y señalad una palabra de cada lista. O inventad el vuestro.</p>'
            '<h2>El Secreto</h2>'
            '<p>Cada persona roba una carta de Secreto y la guarda sin enseñarla: es un objetivo para esta noche. Al final se revelan los dos, y quien haya cumplido el suyo gana una ficha más. Si un Secreto lleva algo que habéis marcado en los NO, se devuelve y se roba otro.</p>'
            '<h2>Durante la noche</h2>'
            f'<p>{e(T["durante"])}</p>'
            '</div>', acN, cabeza=para_todas)

    # ---------- reglas de las aventuras por turnos (prohibiciones, sin rodeos, con guion)
    def antes_turnos(m):
        x, F = X[m], X[m]["fichas"]
        rol = m == "rol"
        cosa, cosas = ("giro", "giros") if rol else ("carta", "cartas")
        items = [
            (f"Recortad los {cosas} de esta aventura y separadlos por escena: cada uno lo dice arriba." if rol else
             "Recortad las cartas de esta aventura y separadlas por escena: cada carta lo dice arriba.") + " Barajad cada mazo y dejadlo boca abajo.",
            f"Mirad juntos los NO y quitad lo que lleve algo marcado: {cosas}, " + ("giros de la historia, " if con_giros(x) else "") + f"Secretos y deseos {de(O['corto'])}.",
            (f"Si queréis, cada persona escribe a solas hasta tres {cosas} secretos en las cartas en blanco, con la escena en la que quiere que salgan, y los baraja en ese mazo sin enseñarlos." if rol else
             "Si queréis, cada persona escribe a solas hasta tres cartas secretas en las cartas en blanco, con la escena en la que quiere que salgan, y las baraja en ese mazo sin enseñarlas."),
            "Cada carta que se lee en voz alta, en su sobre y por orden." + (f" {A['encontrado']['titulo'][:1].upper() + A['encontrado']['titulo'][1:]} va en un sobre aparte: solo se abre cuando un{'' if rol else 'a'} {cosa} lo pida." if m in hay_extra else ""),
        ]
        if rol:
            items.append("Los papeles secretos: separadlos en dos montones, uno por papel, mirando solo la línea de arriba de cada uno, y ordenad cada montón por escenas, boca abajo.")
        if con_giros(x):
            items.append("Los giros de la historia, aparte y boca abajo junto a cada mazo: son opcionales.")
        items.append(f"Las ocho cartas de Secreto, barajadas y boca abajo. Un cuenco con las fichas ({fichas_txt(F)}): "
                     + ("nadie empieza con ninguna." if F["inicial"] == 0 else f"{CUANTAS.get(F['inicial'], F['inicial'])} para cada persona.") + " Y dos llaves.")
        return "".join(f"<li>{e(i)}</li>" for i in items)

    def paso_giros():
        return ('<b>Giros de la historia.</b> Cada escena con mazo trae dos, aparte. Cuando queráis un poco de historia, robad uno y leedlo en voz alta: '
                'si jugáis en personaje, jugadlo; si no, dejadlo pasar.')

    def reglas_turnos(m):
        x, F = X[m], X[m]["fichas"]
        guiada, mazos, final, orac = escenas_de(x)
        rol = m == "rol"
        cuerpo1 = (
            '<div class="cuerpo">'
            f'<h1>{e(x["titulo"])}</h1>'
            f'<p class="lead">{e(x["gancho"])}</p>'
            '<h2>Cómo funciona</h2><ul class="lista">' + "".join(f"<li>{e(r)}</li>" for r in M[m]["reglas"]) + "</ul>"
            f'<h2>Antes de la noche</h2><ul class="casillas">{antes_turnos(m)}</ul></div>')
        p1 = libro.hoja(cuerpo1, ac[m], cabeza=nom(m))
        pasos = [
            f'<b>{e(guiada["corto"])}.</b> {e(T["abre"])} abre el primer sobre, el de {e(lugar(guiada))}, y lee la carta en voz alta. Después, cada persona, a solas, elige {e(T["elige"])} y nombre y roba un Secreto.'
            + (f' Repartid los papeles al azar: {e(minus(T["abre"]))} esconde un montón en cada mano, a la espalda, y su pareja elige mano. Ese montón es suyo toda la noche; ahora, cada cual lee a solas el primer papel.' if rol else '')
            + ' Luego, los gestos que pide la carta.',
            '<b>La Puerta.</b> Cuando acabe la música, las dos llaves a la espalda y, a la de tres, los puños abiertos. Con dos llaves se abre el sobre siguiente. Si falta una, leed en la carta de esa escena lo que dice para cuando la puerta sigue cerrada, y terminad así. Si queréis más tiempo, volved a la escena.',
            ('<b>Las escenas.</b> La carta la lee en voz alta quien no leyó la anterior; poned su música. Después, cada persona lee a solas el papel siguiente de su montón. Por turnos, robáis un giro: quien lo roba lo lee en silencio y lo juega en personaje; si no le convence, va debajo del mazo y roba otro. Si la escena va sola, no hace falta robar.'
             if rol else
             '<b>Las escenas.</b> La carta la lee en voz alta quien no leyó la anterior; poned su música. Empieza quien no ha leído: roba una carta del mazo, la lee en silencio y la hace con su pareja. Si no le convence, va debajo del mazo y roba otra, sin explicar por qué. Después, turno de su pareja. Si se acaba el mazo, seguid sin cartas hasta que acabe la música.'),
        ]
        if m == "explicito":
            pasos += [f'<b>{e(x["etiquetaRegla"])}.</b> Cada escena pone una condición, y la dice su carta: algo que ya no tiene vuelta atrás, como la ropa que no vuelve a ponerse.',
                      f'<b>{e(F["nombre"])}.</b> Cada persona empieza con {e(CUANTAS.get(F["inicial"], F["inicial"]))}. {e(F["explica"])}']
        elif rol:
            pasos.append(f'<b>{e(x["etiquetaRegla"])}.</b> Cada escena tiene un límite que pone la historia, y lo dice su carta. {e(F["explica"])}')
        else:
            pasos.append(f'<b>{e(x["etiquetaRegla"])}.</b> Cada escena prohíbe algo, y lo dice su carta. {e(F["explica"])}')
        if con_giros(x):
            pasos.append(paso_giros())
        cobro = ('Cobrad las fichas por turnos, de una en una: quien cobra pide algo; quien debe lo concede o lo perdona. ' if F["inicial"] == 0
                 else 'Si os quedan fichas, seguid gastándolas. ')
        pasos += [
            f'<b>{e(O["nombre"])}.</b> En {e(lugar(orac))}, antes de la última puerta, consultadlo con las cinco cartas (página {{oraculo}}).',
            f'<b>{e(final["corto"])}.</b> Abrid los sobres pequeños y leed lo que escribisteis antes de empezar. Revelad los Secretos: {e(premio(x))} {cobro}'
            + f'Si queréis, seguid con {"los giros" if rol else "el mazo"} {e(de(lugar(final)))}, por turnos. Si no, ni cartas ni turnos: solo vuestros NO, que valen hasta el amanecer.',
            '<b>El Libro de Visitas.</b> Esta noche o con el café de mañana, cada persona dice tres cosas: el momento que repetiría, una carta que cambiaría y algo que no se atrevió a pedir.',
        ]
        regla_casa = M[m].get("reglaCasa") and not any("te apetece" in r for r in M[m]["reglas"])
        cuerpo2 = ('<div class="cuerpo"><h2 style="margin-top:0">La noche, paso a paso</h2><ol class="pasos' + (' peq' if len(pasos) > 7 else '') + '">' + "".join(f"<li>{p}</li>" for p in pasos) + "</ol>"
                   + ('<div class="recuadro"><div class="rotulo">La regla de la casa</div>Aquí no se pregunta «¿te apetece?». Se pregunta «¿te gusta?».</div>' if regla_casa else '')
                   + f'<h2>Luz y música</h2>{tabla_escenas(x)}</div>')
        p2 = libro.hoja(cuerpo2, ac[m], cabeza=nom(m))
        p3 = libro.hoja(pagina_mesa(m), ac[m], cabeza=nom(m))
        return [p1, p2, p3]

    # ---------- reglas de Encender poco a poco
    def reglas_encender(m):
        x, F = X[m], X[m]["fichas"]
        guiada, mazos, final, orac = escenas_de(x)
        cuerpo1 = (
            '<div class="cuerpo">'
            f'<h1>{e(x["titulo"])}</h1>'
            f'<p class="lead">{e(x["gancho"])}</p>'
            f'<p class="sub">{e(M[m]["corto"])}</p>'
            '<h2>Cómo funciona</h2><ul class="lista">' + "".join(f"<li>{e(r)}</li>" for r in M[m]["reglas"]) + "</ul>"
            '<h2>Antes de la noche</h2><ul class="casillas">'
            '<li>Recortad las cartas de esta aventura. Separadlas por escena y, dentro de cada una, en dos pilas: Seda y Brasa. Barajad cada pila y dejadla boca abajo.</li>'
            f'<li>Mirad juntos los NO y quitad lo que lleve algo marcado: cartas, giros de la historia, cartas de lo que enciende, Secretos y deseos {e(de(O["corto"]))}.</li>'
            '<li>Cada persona coge una carta de Llave, la I o la II, y la deja delante. Sirve para saber a quién le toca recibir.</li>'
            f'<li>Las cartas que se leen en voz alta, en sus sobres y por orden. Los Secretos, barajados. Los giros de la historia, aparte. {e(CUANTAS.get(F["inicial"], F["inicial"]).capitalize())} fichas ({e(fichas_txt(F))}) para cada persona. Y dos llaves.</li></ul>'
            '</div>')
        p1 = libro.hoja(cuerpo1, ac[m], cabeza=nom(m))
        cuerpo2 = (
            '<div class="cuerpo">'
            '<h2 style="margin-top:0">A solas, cada persona</h2><p class="peq sub">Con la hoja privada de la página {privada}, sin que la otra persona mire.</p><ol class="pasos">'
            '<li><b>Lo que te enciende.</b> Repasa las cartas de lo que enciende y quédate con las que quieras; en las cartas en blanco puedes escribir hasta tres más. Barájalas y déjalas boca abajo junto a tu Llave: es tu montón. Tu pareja robará de él, pero nunca lo mirará entero.</li>'
            '<li><b>Lo que te frena.</b> Márcalo en tu hoja. Cuando terminéis, os enseñáis esa parte: es para tenerla presente toda la noche.</li>'
            '<li><b>Tus turnos.</b> Repartid las ocho cartas de turno en dos grupos iguales: cada persona se queda con dos de cada Llave. Elige dos y déjalas boca abajo en el centro; las otras dos vuelven a la caja sin enseñarlas. Dos de tu Llave, si esta noche prefieres recibir; una de cada, si te da igual; dos de la de tu pareja, si prefieres dar. Barajad las cuatro del centro: nadie sabrá qué eligió la otra persona.</li>'
            '<li><b>Cartas secretas.</b> Si quieres, escribe hasta tres en las cartas en blanco, con su escena, su temperatura y si es para regalar (sale cuando das) o para recibir (sale cuando recibes). Barájala en su pila sin enseñarla.</li></ol>'
            f'<h2>Luz y música</h2>{tabla_escenas(x)}'
            '</div>')
        p2 = libro.hoja(cuerpo2, ac[m], cabeza=nom(m))
        pasos = [
            f'<b>{e(guiada["corto"])}.</b> {e(T["abre"])} abre el primer sobre, el de {e(lugar(guiada))}, y lee la carta en voz alta. Después, cada persona, a solas, elige {e(T["elige"])} y nombre y roba un Secreto. Luego, los gestos que pide la carta.',
            '<b>La Puerta.</b> Cuando acabe la música, las llaves a la espalda y, a la de tres, los puños abiertos. Con dos llaves se abre el sobre siguiente. Si falta una, leed en la carta de esa escena lo que dice para cuando la puerta sigue cerrada. Quedarse también es una buena noche.',
            '<b>Cada turno.</b> Girad la carta de turno de arriba: recibe la persona de esa Llave. Quien recibe elige la temperatura, Seda (suave, sin prisa) o Brasa (un poco más); si quiere sorpresa, cierra los ojos. Quien da roba de esa pila, la lee en silencio y la hace. Quien recibe no tiene que hacer nada más que sentir. Cuando se acaben las cuatro cartas de turno, se barajan otra vez.',
            '<b>Más suave que esto.</b> Quien recibe puede pedirlo siempre: entonces se roba de la pila Seda de la escena anterior.',
            '<b>Lo que enciende.</b> Una vez por escena y por persona, quien da puede robar del montón de quien recibe en lugar de la pila de la escena, en el momento que elija.',
            '<b>Cambiar carta.</b> Cualquiera, sin explicar por qué: debajo de la pila y se roba otra. Cambiadla también, sin decir nada, si toca algo que frena a quien recibe: el frío (Hielo), las cosquillas (Pluma), las miradas (Espejo). Una carta escrita a mano que no toca en ese turno va debajo. Si una pila se acaba, elegid la otra temperatura o seguid sin cartas.',
        ] + ([paso_giros()] if con_giros(x) else []) + [
            f'<b>{e(F["nombre"])}.</b> {e(F["explica"])}',
            f'<b>{e(O["nombre"])}.</b> En {e(lugar(orac))}, antes de la última puerta, consultadlo con las cinco cartas (página {{oraculo}}).',
            f'<b>{e(final["corto"])}.</b> Abrid los sobres pequeños y revelad los Secretos: {e(premio(x))} Si queréis, seguid con las pilas {e(de(lugar(final)))}, con las mismas cartas de turno. Si no, ni cartas ni turnos: solo vuestros NO.',
            '<b>El Libro de Visitas.</b> Esta noche o con el café de mañana, cada persona dice el momento que repetiría, una carta que cambiaría y algo que no se atrevió a pedir.',
        ]
        cuerpo3 = ('<div class="cuerpo"><h2 style="margin-top:0">La noche, paso a paso</h2><ol class="pasos peq">' + "".join(f"<li>{p}</li>" for p in pasos) + "</ol>"
                   '<div class="recuadro"><div class="rotulo">La regla de la casa</div>Aquí no se pregunta «¿te apetece?». Se pregunta «¿te gusta?».</div>'
                   '</div>')
        p3 = libro.hoja(cuerpo3, ac[m], cabeza=nom(m))
        p4 = libro.hoja(pagina_mesa(m), ac[m], cabeza=nom(m))
        return [p1, p2, p3, p4]

    def pagina_mesa(m):
        x = X[m]
        B, rol = m == "encender", m == "rol"
        if rol:
            cosas = "Los giros de esta aventura, los papeles secretos, los Secretos y las cartas en blanco"
        else:
            cosas = "Las cartas de juego de esta aventura, los Secretos y las cartas en blanco"
            if B:
                cosas += ", las de lo que enciende, las de turno y las dos Llaves"
            if con_giros(x):
                cosas += ", y los giros de la historia"
        imprimir = [
            cosas + f" (páginas {{naipes_{m}}}).",
            f"Las cartas que se leen en voz alta (páginas {{cartas_{m}}}) y sus rótulos (página {{rotulos_{m}}})"
            + (f"; también {A['encontrado']['titulo']} (página {{encontrada}})" if m in hay_extra else "") + ".",
            f"Los deseos y las cinco cartas {de(O['corto'])} (páginas {{oraculo_cartas}}).",
            f"Las fichas de papel (página {{fichas}}), si no tenéis {T['monedas']}.",
        ] + (["Dos hojas privadas, una por persona (página {privada})."] if B else []) + [
            f"La invitación (página {{invitacion_{m}}}), si queréis entregarla con tiempo.",
        ]
        mesa = ("<p>Los sobres, cerrados y en orden. Los mazos de cada escena, boca abajo y separados"
                + (", con Seda a un lado y Brasa al otro" if B else "")
                + ". El cuenco de fichas, los Secretos y las cinco cartas " + e(de(O["corto"])) + " a mano. "
                + ("Los dos montones de papeles, boca abajo y en orden. " if rol else "")
                + ("Cada persona, su Llave delante y su montón de lo que enciende al lado; las cuatro cartas de turno, barajadas en el centro. " if B else "")
                + "Las llaves, en el bolsillo. El móvil, lejos, salvo para la música.</p>")
        return ('<div class="cuerpo"><h2 style="margin-top:0">Lo que hace falta</h2>' + material_html(x)
                + '<h2>Para imprimir y recortar</h2><ul class="casillas">' + "".join(f"<li>{e(i)}</li>" for i in imprimir) + "</ul>"
                + '<h2>En la mesa, al empezar</h2>' + mesa + '</div>')

    def hoja_privada(m):
        frenos = "".join(f"<li>{e(f['label'])}</li>" for f in D["FRENOS"])
        def mitad(pos):
            return (f'<div class="mitad {pos}"><div class="dentro">'
                    '<h2 style="margin-top:0">Solo para ti</h2>'
                    '<p class="peq sub">Rellénala a solas. Lo que te enciende va en las cartas; aquí, lo que te frena.</p>'
                    f'<h3>Lo que me frena</h3><ul class="casillas dos-col peq">{frenos}</ul>'
                    '<p class="peq">Otra cosa: <span class="linea-rellenar" style="min-width:110mm"></span></p>'
                    '<p class="peq sub">Cuando las dos personas terminéis, enseñaos esta hoja: es para tenerla presente toda la noche. Si algo frena, se para o se cambia, sin explicaciones y sin reproches.</p>'
                    '<p class="peq"><i>Y además, a solas:</i> elige tus cartas de lo que enciende, tus dos cartas de turno y, si quieres, tus cartas secretas.</p>'
                    '</div></div>')
        return libro.hoja(mitad("arriba") + '<div class="corte-medio"></div>' + mitad("abajo"), ac[m], pie=False)

    # ---------- cartas que se leen en voz alta
    PLIEGUES = ('<div class="pliegue" style="left:0;top:99mm"></div><div class="pliegue" style="right:0;top:99mm"></div>'
                '<div class="pliegue" style="left:0;top:198mm"></div><div class="pliegue" style="right:0;top:198mm"></div>')

    def carta_escena(m, s):
        x, acento = X[m], ac[m]
        lectura = s.get("lectura") or "La lee en voz alta quien no leyó la anterior."
        antes = f'Antes de leer: {minus(s["luz"])}. Música: {minus(s["musica"])}.'
        parrafos = "".join(f'<p{" class=\"fecha\"" if k == 0 and s.get("fecha") else ""}>{e(p)}</p>' for k, p in enumerate(s["carta"]))
        bloques = ""
        if s.get("regla"):
            bloques += f'<div class="recuadro"><div class="rotulo">{e(x["etiquetaRegla"])}</div>{e(s["regla"])}</div>'
        if s.get("papeles") and s["tipo"] != "guiada":
            bloques += '<div class="recuadro peq"><div class="rotulo">Los papeles</div>Antes de jugar la escena, cada persona lee a solas el papel siguiente de su montón.</div>'
        if s.get("pasos"):
            bloques += '<div class="recuadro"><div class="rotulo">Para empezar</div><ol class="pasos" style="margin:0">' + "".join(f'<li><b>{e(p["t"])}.</b> {e(p["d"])}</li>' for p in s["pasos"]) + "</ol></div>"
        if s.get("cerrada"):
            bloques += f'<div class="recuadro peq"><div class="rotulo">Si después la puerta sigue cerrada</div>{e(s["cerrada"])}</div>'
        if s["tipo"] == "final":
            F = x["fichas"]
            bloques += ('<div class="recuadro peq"><div class="rotulo">Antes de que el juego se retire</div>'
                        f'Revelad los Secretos: {e(premio(x))} Recordad lo que dijo {e(O["corto"])}. '
                        + ("Las fichas se cobran por turnos: quien cobra pide algo y quien debe lo concede o lo perdona. " if F["inicial"] == 0
                           else "Si os quedan fichas, seguid gastándolas. ")
                        + f'Si queréis, seguid con {"los giros" if m == "rol" else "las cartas"} {e(de(lugar(s)))}.</div>')
        return libro.hoja(
            PLIEGUES + '<div class="cuerpo">'
            f'<div class="sobre">{e(s["sobre"])}</div><div class="antes">{e(lectura)} {e(antes)}</div>'
            f'<div class="texto">{parrafos}</div>'
            + (f'<div class="firma">{e(s["firma"])}</div>{sello_svg(acento)}' if s.get("firma") else "")
            + bloques + '</div>', acento, clase="carta-hoja", cabeza="", pie=False)

    def carta_encontrada():
        en = A["encontrado"]
        parrafos = "".join(f"<p>{e(p)}</p>" for p in en["parrafos"])
        return libro.hoja(PLIEGUES + '<div class="cuerpo">'
                          f'<div class="sobre">{e(en["titulo"][:1].upper() + en["titulo"][1:])}</div><div class="antes">No se abre hasta que lo pida {"un giro o una carta" if "rol" in hay_extra and len(hay_extra) > 1 else ("un giro" if hay_extra == ["rol"] else "una carta")}. Se lee despacio, cerca del oído.</div>'
                          f'<div class="texto">{parrafos}</div>{sello_svg(acN)}</div>', acN, clase="carta-hoja", pie=False)

    # ---------- naipes
    def etiquetas(obj):
        return ", ".join(etq[x]["n"] for x in obj.get("tags", []))

    def secreto(sec, pie):
        return naipe("Secreto", "", e(sec["t"]), f'<p><i>{e(sec["m"])}</i></p><p><b>Tu objetivo:</b> {e(sec["o"])}</p>', etiquetas(sec), pie)

    def giros_de(x, pie):
        out = []
        for s in x["escenas"]:
            for g in s.get("giros", []):
                out.append(naipe("Giro · " + e(s["corto"]), "", e(g["t"]), f'<p>{e(con_pareja(g["x"]))}</p>', etiquetas(g), "Giro de la historia"))
        return out

    def naipes_turnos(m):
        x, pie = X[m], nom(m)
        out = []
        for s in x["escenas"]:
            for c in s.get("cartas", []):
                out.append(naipe(e(s["nombre"]), pips(c["n"]), e(c["t"]), f'<p>{e(c["x"])}</p>', etiquetas(c), pie))
        out += giros_de(x, pie)
        if m == "rol":
            for s in x["escenas"]:
                for p in s.get("papeles", []):
                    out.append(naipe(e(p["t"]), "Papel", e(s["nombre"]), "".join(f"<p>{e(par)}</p>" for par in p["x"]), "", "Solo para quien lleva este papel", "papel"))
        for k in range(6):
            out.append(naipe("Giro secreto" if m == "rol" else "Carta secreta", "", "", '<p class="campo">Escena: ________________</p><div class="renglones"></div>', "", pie))
        for sec in x["secretos"]:
            out.append(secreto(sec, pie))
        return out

    def llaves_mini():
        return D["LLAVES_SVG"].replace('class="llaves"', 'class="llave-dib"')

    def naipes_encender(m):
        x = X[m]
        out = []
        for s in x["escenas"]:
            for c in s.get("cartas", []):
                out.append(naipe(e(s["nombre"]), temp(c["temp"]), e(c["t"]), f'<p>{e(con_pareja(c["x"]))}</p>', etiquetas(c), "Encender"))
        out += giros_de(x, "Encender")
        for a in D["ACELERANTES"]:
            out.append(naipe("Algo que enciende a tu pareja", "", e(a["label"]), f'<p>{e(con_pareja(a["carta"]))}</p>', etiquetas(a), "Lo que enciende"))
        for k in range(6):
            out.append(naipe("Algo que enciende a tu pareja", "", "", '<p class="campo">Lo escribió así. Haz que pase, sin prisa:</p><div class="renglones"></div>', "", "Lo que enciende"))
        for k in range(6):
            out.append(naipe("Carta secreta", "", "",
                             '<p class="campo">Escena: ______________</p><p class="campo">Seda □ &nbsp;&nbsp; Brasa □</p><p class="campo">Para regalar □ &nbsp;&nbsp; Para recibir □</p><p class="campo">De la Llave: I □ &nbsp;&nbsp; II □</p><div class="renglones"></div>', "", "Encender"))
        for dueño in ("I", "II"):
            for quien in ("I", "I", "II", "II"):
                out.append(naipe("Carta de turno", "", "", f'<div class="centro">{llaves_mini()}<div class="grande">{quien}</div><p>Recibe la Llave {quien}</p></div>', "", "Encender"))
        for quien in ("I", "II"):
            out.append(naipe("Llave", "", "", f'<div class="centro">{llaves_mini()}<div class="grande">{quien}</div><p class="peq">Déjala delante de ti. Tu montón de lo que te enciende va a su lado, boca abajo.</p></div>', "", "Encender"))
        for sec in x["secretos"]:
            out.append(secreto(sec, "Encender"))
        for k in range((-len(out)) % 9):
            out.append(naipe("Algo que enciende a tu pareja", "", "", '<p class="campo">Lo escribió así. Haz que pase, sin prisa:</p><div class="renglones"></div>', "", "Lo que enciende"))
        return out

    def naipes_oraculo():
        out = []
        for d in D["ORACULO"]:
            if d.get("modo") and d["modo"] not in modos:
                continue
            pie = "Deseo · solo en " + nom(d["modo"]) if d.get("modo") else "Deseo"
            out.append(naipe(e(O["nombre"]), "", "", f'<p style="font-size:11pt;line-height:1.38;margin-top:6mm">{e(d["x"])}</p>', etiquetas(d), pie))
        for k in range(6):
            out.append(naipe(e(O["nombre"]), "", "", '<p style="font-size:11pt;margin-top:6mm">Esta noche, …</p><div class="renglones"></div>', "", "Deseo en blanco"))
        for k in range(3):
            out.append(naipe(e(O["nombre"]), "", "", '<div class="centro"><div class="grande" style="font-size:64pt;margin-top:11mm;color:#A3242E">♥</div><p>Roja</p>' + ('<p class="peq sub">El Corazón: va en el centro.</p>' if k == 0 else '<p class="peq sub">Una para cada persona.</p>') + "</div>", "", "Cinco cartas"))
        for k in range(2):
            out.append(naipe(e(O["nombre"]), "", "", '<div class="centro"><div class="grande" style="font-size:64pt;margin-top:11mm;color:#1E1E1E">♠</div><p>Negra</p><p class="peq sub">Una para cada persona.</p></div>', "", "Cinco cartas"))
        return out

    def pagina_oraculo():
        pasos = [
            "Cada persona toma una roja y una negra. La tercera roja, el Corazón, va boca abajo en el centro.",
            "En secreto, cada persona pone sus dos cartas boca abajo a su lado del Corazón. Si lo deseas, tu roja toca el Corazón; si no, va hacia fuera.",
            "Recoged las cinco en orden y cortad varias veces, cada persona mientras la otra cierra los ojos.",
            "Repartidlas en círculo, en orden, y giradlas. Si las tres rojas quedan juntas, el deseo es de las dos personas.",
        ]
        solo = [m for m in modos if any(d.get("modo") == m for d in D["ORACULO"])]
        aviso = (" y los que digan «solo en " + " o ".join(nom(m) for m in solo) + "» si jugáis otra aventura") if solo else ""
        return libro.hoja(
            '<div class="cuerpo">'
            f'<h1>{e(O["nombre"])}</h1>'
            '<p class="lead">Descubre lo que deseáis a la vez sin revelar lo que solo desea una persona: si tú quieres algo y tu pareja no, nunca sabrá que lo querías.</p>'
            '<h2>Antes de consultarlo</h2>'
            f'<p>Quitad los deseos con algo marcado en los NO{e(aviso)}, barajad los demás y robad seis. Si queréis, añadid hasta dos escritos por vosotros en los deseos en blanco.</p>'
            '<h2>Con cinco cartas</h2><p>Para cada deseo, uno a uno, leedlo en voz alta y después:</p>'
            '<ol class="pasos">' + "".join(f"<li>{e(p)}</li>" for p in pasos) + "</ol>"
            '<p>Si el deseo es de las dos personas, dejadlo boca arriba a la vista. Si no, '
            f'{e(O["corto"])} calla, el deseo vuelve a la caja y nadie pregunta por qué.</p>'
            '<div class="recuadro"><div class="rotulo">Por qué funciona</div>'
            'Las tres rojas solo quedan juntas si las dos personas pusieron su roja tocando el Corazón. Cortar no cambia el orden en círculo, así que el resultado se ve, pero no quién dijo que no.</div>'
            '<p class="peq sub">Lo que dice no obliga a nada: es una pista de por dónde puede seguir la noche. Si marcaste algo que no aparece, ya sabes la respuesta.</p>'
            '<p class="peq sub">Las cinco cartas están en las hojas de cartas siguientes; también sirven tres rojas y dos negras de cualquier baraja con el mismo dorso.</p>'
            '</div>', acN, cabeza=para_todas)

    def pagina_fichas():
        simb = {"carnaval": "V", "fantasia": "☾"}.get(amb)
        dibujo = e(simb) if simb else f'<svg viewBox="0 0 40 40" style="width:9mm;height:9mm" fill="currentColor">{LLAVE_PATHS}</svg>'
        tipos = []   # [fichas, color, modos que las usan]
        for m in modos:
            F = X[m]["fichas"]
            ya = next((tp for tp in tipos if tp[0]["nombre"] == F["nombre"]), None)
            if ya:
                ya[2].append(m)
            else:
                tipos.append([F, ac[m], [m]])
        cel = [f'<div class="ficha" style="--acento:{color}"><b>{dibujo}</b><span>{e(F["una"])}</span></div>'
               for F, color, ms in tipos for k in range(12)]
        leyenda = "; ".join(f'{e(fichas_txt(F))} ({e(" y ".join(nom(m) for m in ms))})' for F, c_, ms in tipos)
        return libro.hoja(
            f'<div class="cabeza">{e(para_todas)}</div>'
            f'<div class="fichas">{"".join(cel)}</div>'
            f'<div style="position:absolute;left:31mm;right:31mm;bottom:17mm" class="peq sub">Fichas de papel, por si no tenéis {e(T["monedas"])}. Doce de cada clase, por filas: {leyenda}.</div>',
            acN, pie=True)

    def paginas_rotulos():
        def celda(m, s):
            lectura = s.get("lectura") or "La lee en voz alta quien no leyó la anterior."
            return (f'<div class="rotulo-sobre" style="--acento:{ac[m]}"><div class="modo">{e(nom(m))}</div><div class="display">{e(s["sobre"])}</div>'
                    f'<p>{e(lectura)} Antes de abrirla: {e(minus(s["luz"]))}.</p></div>')

        def celda_enc(m):
            tit = A["encontrado"]["titulo"]
            return (f'<div class="rotulo-sobre" style="--acento:{ac[m]}"><div class="modo">{e(nom(m))}</div><div class="display">{e(tit[:1].upper() + tit[1:])}</div>'
                    f'<p>No se abre hasta que {"un giro" if m == "rol" else "una carta"} lo pida.</p></div>')
        grupos, actual, ms = [], [], []
        for m in modos:
            b = [celda(m, s) for s in X[m]["escenas"]] + ([celda_enc(m)] if m in hay_extra else [])
            if actual and len(actual) + len(b) > 12:
                grupos.append((actual, ms))
                actual, ms = [], []
            actual, ms = actual + b, ms + [m]
        if actual:
            grupos.append((actual, ms))
        pag = {}
        for cel, ms in grupos:
            n = libro.hoja(f'<div class="cabeza">{e(" y ".join(nom(m) for m in ms))}</div><h2 style="position:absolute;left:17mm;top:15mm;margin:0">Rótulos para los sobres</h2>'
                           f'<div class="rotulos">{"".join(cel)}</div>', acN)
            for m in ms:
                pag[m] = n
        return pag

    def paginas_invitaciones():
        def inv(m, pos):
            x, mm = X[m], M[m]
            antes = ("Escribe una carta para mí y ciérrala en un sobre pequeño; no se abrirá hasta el final."
                     + (" Piensa también qué te enciende y qué te frena: el juego te lo preguntará en secreto." if mm["pideFrenos"] else "")
                     + " " + (A.get("prepara") or "Prepárate como para una cita con alguien a quien no conoces."))
            return (f'<div class="mitad {pos}" style="--acento:{ac[m]}"><div class="dentro">'
                    '<p>Para <span class="linea-rellenar"></span></p>'
                    f'<h2 style="margin-top:2mm">{e(x["titulo"])}</h2><p class="lead" style="font-size:11pt">{e(x["gancho"])}</p>'
                    f'<p class="peq"><b>Qué es:</b> {e(mm["invitacion"][0].upper() + mm["invitacion"][1:])} Dura unas dos horas.</p>'
                    f'<p class="peq"><b>Antes de la noche:</b> {e(antes)}</p>'
                    '<p class="peq"><b>Lo importante:</b> Puedes decir que no ahora o en cualquier momento de la noche, sin dar explicaciones. No hay ninguna meta que alcanzar.</p>'
                    '<p class="peq"><b>Cuándo:</b> <span class="linea-rellenar" style="min-width:70mm"></span></p>'
                    '<p class="peq" style="text-align:right;margin-top:4mm">— <span class="linea-rellenar" style="min-width:40mm"></span></p>'
                    '</div></div>')
        pag = {}
        for i in range(0, len(modos), 2):
            par = modos[i:i + 2]
            html_ = inv(par[0], "arriba") + ('<div class="corte-medio"></div>' + inv(par[1], "abajo") if len(par) > 1 else "")
            n = libro.hoja(html_, acN, pie=False)
            for m in par:
                pag[m] = n
        return pag

    def pagina_dorsos():
        un = f'<div class="dorso"><div class="fondo"></div><div class="medalla">{D["LLAVES_SVG"]}<span>Doble Llave</span></div></div>'
        return libro.hoja(f'<div class="rejilla">{un * 9}</div>', acN, pie=False)

    def rango(l):
        return str(l[0]) if len(l) == 1 else f"{l[0]}–{l[-1]}"

    # ---------- orden del libro
    portada()
    libro.paginas.append(None)  # hueco para «Antes de imprimir»
    paginas, refs = {}, {}
    ini = len(libro.paginas) + 1
    comun_siempre(); comun_antes(); comun_mascaras()
    paginas["comun"] = (ini, len(libro.paginas))
    for m in modos:
        ini = len(libro.paginas) + 1
        if m == "encender":
            reglas_encender(m)
            refs["{privada}"] = hoja_privada(m)
        else:
            reglas_turnos(m)
        cartas = [carta_escena(m, s) for s in X[m]["escenas"]]
        naipes = hojas_de_naipes(libro, naipes_encender(m) if m == "encender" else naipes_turnos(m), ac[m], "")
        refs[f"{{cartas_{m}}}"] = rango(cartas)
        refs[f"{{naipes_{m}}}"] = rango(naipes)
        paginas[m] = (ini, len(libro.paginas))
    ini = len(libro.paginas) + 1
    refs["{oraculo}"] = pagina_oraculo()
    refs["{oraculo_cartas}"] = rango(hojas_de_naipes(libro, naipes_oraculo(), acN, ""))
    if hay_extra:
        refs["{encontrada}"] = carta_encontrada()
    refs["{fichas}"] = pagina_fichas()
    for m, n in paginas_rotulos().items():
        refs[f"{{rotulos_{m}}}"] = n
    for m, n in paginas_invitaciones().items():
        refs[f"{{invitacion_{m}}}"] = n
    pagina_dorsos()
    paginas["final_comun"] = (ini, len(libro.paginas))

    guardadas = libro.paginas
    libro.paginas = guardadas[:1]
    como_usar(paginas)
    libro.paginas = libro.paginas + guardadas[2:]

    cuerpo = "".join(libro.paginas)
    for k, v in refs.items():
        cuerpo = cuerpo.replace(k, str(v))
    quedan = sorted(set(re.findall(r"\{[a-z_]+\}", cuerpo)))
    if quedan:
        raise SystemExit(f"{amb}: referencias sin resolver: {quedan}")
    if amb == "cotidiana":
        cuerpo = a_tarde(cuerpo)
    doc = (f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Doble Llave · {e(A["nombre"])}</title>'
           f'<style>{css(t)}</style></head><body>{cuerpo}</body></html>')
    return doc, paginas


# ---------------------------------------------------------------- render
async def a_pdf(html_path, pdf_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        b = await pw.chromium.launch(**CHROME)
        page = await b.new_page()
        await page.goto(html_path.as_uri())
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(300)
        problemas = await page.evaluate("""() => {
          const out = [];
          document.querySelectorAll('.hoja').forEach((h, i) => {
            h.querySelectorAll('.cuerpo, .dentro, .n-txt, .rotulo-sobre').forEach(el => {
              if(el.scrollHeight > el.clientHeight + 1) out.push('pág. ' + (i + 1) + ': ' + el.className + ' se sale ' + (el.scrollHeight - el.clientHeight) + 'px · ' + el.textContent.trim().slice(0, 60));
            });
          });
          const fuentes = [...document.fonts].filter(f => f.status === 'error').map(f => f.family);
          if(fuentes.length) out.push('fuentes que no cargan: ' + fuentes.join(', '));
          return out;
        }""")
        await page.pdf(path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True,
                       margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        await b.close()
        return problemas


def main():
    D = exportar_datos()
    SALIDA.mkdir(exist_ok=True)
    nombres = {"carnaval": "doble-llave-carnaval-para-imprimir", "fantasia": "doble-llave-bosque-para-imprimir",
               "cotidiana": "doble-llave-cotidiana-para-imprimir"}
    total_problemas = 0
    solo = sys.argv[1:] or list(nombres)
    for amb in solo:
        doc, paginas = construir(D, amb)
        hp = PRINT / f"{nombres[amb]}.html"
        hp.write_text(doc, encoding="utf-8")
        pdf = SALIDA / f"{nombres[amb]}.pdf"
        problemas = asyncio.run(a_pdf(hp, pdf))
        print(f"{pdf.name}: secciones {paginas}")
        for p in problemas:
            print("  ", p)
        total_problemas += len(problemas)
    sys.exit(1 if total_problemas else 0)


if __name__ == "__main__":
    main()

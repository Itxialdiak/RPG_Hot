#!/usr/bin/env python3
"""Valida los paquetes de cartas (cartas/*.json) y los inyecta en doble-llave.html.

La plantilla (build/plantilla.html) conserva el hueco `const CARTAS = {/*CARTAS*/};`
para poder reconstruir la app cada vez que se toquen las cartas.
"""
import json, re, shutil, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
APP = RAIZ / "doble-llave.html"
PLANTILLA = RAIZ / "build" / "plantilla.html"
HUECO = "const CARTAS = {/*CARTAS*/};"

ESCENAS = {
    "carnaval/prohibicion": (["salon", "galeria", "biblioteca"], "alcoba"),
    "carnaval/encender": (["musica", "banquete", "banos"], "alcoba"),
    "fantasia/prohibicion": (["corro", "lago", "gruta"], "enramada"),
    "fantasia/encender": (["aire", "agua", "tierra"], "fuego"),
    "cotidiana/prohibicion": (["cocina", "salon", "apagon"], "dormitorio"),
    "cotidiana/encender": (["cocina", "bano", "apagon"], "dormitorio"),
}
# Los modos nuevos se añaden aquí a medida que existen sus cartas.
MODOS_NUEVOS = {
    "carnaval/explicito": (["ridotto", "aretino", "casino"], "alcoba"),
    "carnaval/rol": (["salon", "galeria", "biblioteca"], "alcoba"),
    "fantasia/explicito": (["hogueras", "mayo", "helechos"], "amanecer"),
    "fantasia/rol": (["corro", "lago", "gruta"], "enramada"),
    "cotidiana/explicito": (["entrada", "sofa", "ducha"], "dormitorio"),
    "cotidiana/rol": (["cocina", "salon", "apagon"], "dormitorio"),
}
ESCENAS.update(MODOS_NUEVOS)
PAQUETES = sorted({am.replace("/", "-") for am in ESCENAS})
TURNOS = ("prohibicion", "explicito", "rol")   # se juegan por turnos: cartas con nivel (n), sin {R}

# Palabras que delatan masculino genérico o adjetivos que concuerdan con quien juega.
GENERO = re.compile(r"\b(juntos|juntas|abrazados|abrazadas|quietos|quietas?|quieto|desnud[oa]s?|vendad[oa]s?|tumbad[oa]s?|"
                    r"solos|solas|cada uno|cada una|vosotros|vosotras|ninguno|ninguna|el otro|la otra|los dos|las dos|"
                    r"todos|todas|list[oa]s?|atent[oa]s?|pegad[oa]s?|dispuest[oa]s?|cansad[oa]s?|encantad[oa]s?|"
                    r"tranquil[oa]s?|nervios[oa]s?|excitad[oa]s?|él|ella|ellos|ellas|chico|chica|hombre|mujer|"
                    r"novio|novia|marido|esposa|amante)\b", re.I)
# Excepciones revisadas a mano: el adjetivo concuerda con un sustantivo, no con una persona.
GENERO_OK = [
    "manos quietas", "dejar las manos quietas", "La Manos Quietas", "Las Manos Quietas",
    "las dos personas", "a la otra persona", "la otra persona", "boca pegada",
]
# Las ataduras consentidas sí caben (con su propio NO); lo que se vigila es el lenguaje de dominación.
SUMISION = re.compile(r"\b(mand[ao]s?|obedec\w*|orden[ae]s?|sumis\w*|domin(?!go)\w*|esposas|"
                      r"castig\w*|conquist\w*|caza\w*|presa|amo|ama|esclav\w*|rendirse|se rinde)\b", re.I)
EXPLICITO = re.compile(r"\b(pene|vagina|vulva|cl[ií]toris|pez[oó]n\w*|genital\w*|penetr\w*|orgasm\w*|corr[ea]rse|"
                       r"masturb\w*|sexo oral|co[ñn]o|polla|culo|nalgas|teta\w*|pecho desnudo)\b", re.I)
# Sin rodeos nombra las cosas (también sugiere la penetración), pero sin palabras soeces, sin anatomía con género
# y sin instrucciones de dónde ni cómo: eso último no lo detecta una expresión regular y se revisa a mano.
EXPLICITO_DURO = re.compile(r"\b(pene|vagina|vulva|cl[ií]toris|testículo\w*|genital\w*|corr[ea]rse|"
                            r"co[ñn]o|polla|culo|teta\w*|follar\w*|chupar\w*|mamada\w*|semen|eyacul\w*)\b", re.I)


def avisos_texto(clave, c):
    out = []
    x = c["t"] + " " + c["x"]
    vocab = EXPLICITO_DURO if "/explicito/" in clave else EXPLICITO
    for m in GENERO.finditer(x):
        trozo = x[max(0, m.start() - 12): m.end() + 12]
        if not any(ok.lower() in trozo.lower() for ok in GENERO_OK):
            out.append(f"GÉNERO  {clave} {c['id']}: «{m.group(0)}» … {trozo!r}")
    for m in SUMISION.finditer(x):
        out.append(f"SUMISIÓN {clave} {c['id']}: «{m.group(0)}»")
    for m in vocab.finditer(x):
        out.append(f"EXPLÍCITO {clave} {c['id']}: «{m.group(0)}»")
    return out


def main():
    if not PLANTILLA.exists():
        src = APP.read_text(encoding="utf-8")
        if HUECO not in src:
            sys.exit("Ni plantilla ni hueco en la app: no sé dónde inyectar.")
        PLANTILLA.write_text(src, encoding="utf-8")
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    assert plantilla.count(HUECO) == 1, "La plantilla debe tener exactamente un hueco."

    etiquetas = set(re.findall(r'\{id:"([a-z]+)", n:"', plantilla[plantilla.find("const ETIQUETAS"):plantilla.find("const SENALES")]))
    cartas, errores, avisos, resumen = {}, [], [], []
    for nombre in PAQUETES:
        datos = json.loads((RAIZ / "cartas" / f"{nombre}.json").read_text(encoding="utf-8"))
        for k, v in datos.items():
            if k in cartas:
                errores.append(f"Clave repetida entre paquetes: {k}")
            cartas[k] = v

    for am, (mazos, final) in ESCENAS.items():
        modo = am.split("/")[1]
        ids = {}
        for esc in mazos + [final]:
            k = f"{am}/{esc}"
            lista = cartas.get(k)
            if lista is None:
                errores.append(f"Falta el mazo {k}")
                continue
            esperado = (6, 9) if esc == final else (8, 10)
            if not esperado[0] <= len(lista) <= esperado[1]:
                errores.append(f"{k}: {len(lista)} cartas (esperaba entre {esperado[0]} y {esperado[1]})")
            for c in lista:
                for campo in ("id", "t", "tags", "x"):
                    if campo not in c:
                        errores.append(f"{k} {c.get('id')}: falta «{campo}»")
                if c["id"] in ids:
                    errores.append(f"{am}: id repetido {c['id']} ({ids[c['id']]} y {esc})")
                ids[c["id"]] = esc
                for t in c["tags"]:
                    if t not in etiquetas:
                        errores.append(f"{k} {c['id']}: etiqueta desconocida «{t}»")
                if len(set(c["tags"])) != len(c["tags"]):
                    errores.append(f"{k} {c['id']}: etiqueta duplicada")
                if modo in TURNOS:
                    if "{R}" in c["x"]:
                        errores.append(f"{k} {c['id']}: {{R}} en un modo por turnos")
                    if c.get("n") not in (1, 2, 3, 4):
                        errores.append(f"{k} {c['id']}: n inválido")
                    if esc == final and c.get("n") != 4:
                        errores.append(f"{k} {c['id']}: el final debe ser n4")
                else:
                    if c.get("temp") not in ("seda", "brasa"):
                        errores.append(f"{k} {c['id']}: temp inválida")
                if len(c["x"]) > 330:
                    avisos.append(f"LARGA    {k} {c['id']}: {len(c['x'])} caracteres")
                avisos += avisos_texto(k, c)
            if modo == "encender" and lista:
                seda = sum(c.get("temp") == "seda" for c in lista)
                brasa = len(lista) - seda
                minimo = 3 if esc == final else 4
                if seda < minimo or brasa < minimo or abs(seda - brasa) > 1:
                    errores.append(f"{k}: {seda} Seda / {brasa} Brasa (desequilibrado)")
            sobreviven = [c["id"] for c in lista if not {"desnudez", "intimo"} & set(c["tags"])]
            resumen.append(f"{k:32} {len(lista)} cartas · sin Desnudez ni Zonas íntimas quedan {len(sobreviven)}: {', '.join(sobreviven)}")

    # Giros de la historia (opcionales, en las escenas con mazo de los modos con cartas)
    giros = {}
    for f in sorted((RAIZ / "cartas").glob("*-giros.json")):
        for k, v in json.loads(f.read_text(encoding="utf-8")).items():
            am, esc = k.rsplit("/", 1)
            if am not in ESCENAS or esc not in ESCENAS[am][0]:
                errores.append(f"Giros en una escena sin mazo: {k}")
                continue
            ids = set()
            for g in v:
                for campo in ("id", "t", "tags", "x"):
                    if campo not in g:
                        errores.append(f"giro {k} {g.get('id')}: falta «{campo}»")
                if g["id"] in ids:
                    errores.append(f"giro {k}: id repetido {g['id']}")
                ids.add(g["id"])
                for t in g["tags"]:
                    if t not in etiquetas:
                        errores.append(f"giro {k} {g['id']}: etiqueta desconocida «{t}»")
                if "{R}" in g["x"]:
                    errores.append(f"giro {k} {g['id']}: {{R}} en un giro")
                if len(g["x"]) > 330:
                    avisos.append(f"LARGO    giro {k} {g['id']}: {len(g['x'])} caracteres")
                avisos += avisos_texto(k, g)
            giros[k] = v
    if giros:
        resumen.append(f"Giros de la historia: {sum(len(v) for v in giros.values())} en {len(giros)} escenas")

    sobrantes = set(cartas) - {f"{am}/{e}" for am, (m, f) in ESCENAS.items() for e in m + [f]}
    for k in sorted(sobrantes):
        errores.append(f"Mazo sin escena: {k}")

    print("\n".join(resumen))
    if avisos:
        print("\nAvisos para revisar a mano:")
        print("\n".join(avisos))
    if errores:
        print("\nERRORES:")
        print("\n".join(errores))
        sys.exit(1)

    # La escapada: base + 12 combinaciones, validadas aparte
    import escapada as esc
    datos_esc, err_esc, avisos_esc, resumen_esc = esc.cargar(completo=True)
    if err_esc:
        print("\nERRORES EN LA ESCAPADA:"); print("\n".join(err_esc)); sys.exit(1)
    print("\n" + "\n".join(resumen_esc))

    lineas = ["const CARTAS = {"]
    claves = list(cartas)
    for i, k in enumerate(claves):
        lineas.append(f'  {json.dumps(k, ensure_ascii=False)}: [')
        for j, c in enumerate(cartas[k]):
            fin = "," if j < len(cartas[k]) - 1 else ""
            lineas.append("    " + json.dumps(c, ensure_ascii=False, separators=(",", ":")) + fin)
        lineas.append("  ]" + ("," if i < len(claves) - 1 else ""))
    lineas.append("};")
    salida = plantilla.replace(HUECO, "\n".join(lineas))
    HUECO_G = "const GIROS = {/*GIROS*/};"
    if HUECO_G in salida:
        cuerpo = ",\n".join(f'  {json.dumps(k, ensure_ascii=False)}: [\n' + ",\n".join("    " + json.dumps(g, ensure_ascii=False, separators=(",", ":")) for g in v) + "\n  ]" for k, v in giros.items())
        salida = salida.replace(HUECO_G, "const GIROS = {\n" + cuerpo + "\n};")
    HUECO_ESC = "const ESCAPADA = {/*ESCAPADA*/};"
    if HUECO_ESC in salida:
        def una_por_linea(lista, sangria):
            return "[\n" + ",\n".join(sangria + json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in lista) + "\n" + sangria[:-2] + "]"
        cuerpo = {k: v for k, v in datos_esc.items() if k not in ("propuestas", "combos")}
        partes = [f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}" for k, v in cuerpo.items()]
        partes.append('  "propuestas": ' + una_por_linea(datos_esc["propuestas"], "    "))
        combos = []
        for k, c in datos_esc["combos"].items():
            resto = {kk: vv for kk, vv in c.items() if kk != "propuestas"}
            txt = json.dumps(resto, ensure_ascii=False)[:-1] + ', "propuestas": ' + una_por_linea(c["propuestas"], "      ") + "}"
            combos.append(f"    {json.dumps(k)}: {txt}")
        partes.append('  "combos": {\n' + ",\n".join(combos) + "\n  }")
        salida = salida.replace(HUECO_ESC, "const ESCAPADA = {\n" + ",\n".join(partes) + "\n};")
    # La música: catálogo de musica/catalogo.json (los archivos los trae herramientas/musica.mjs)
    HUECO_MU = "const MUSICA = {/*MUSICA*/};"
    if HUECO_MU in salida:
        cat = json.loads((RAIZ / "musica" / "catalogo.json").read_text(encoding="utf-8"))
        err_mu = []
        for lid, l in cat["listas"].items():
            for pid in l["pistas"]:
                if pid not in cat["pistas"]:
                    err_mu.append(f"Lista {lid}: pista desconocida {pid}")
        bloque = plantilla[plantilla.find("const LISTAS_ESCENA"):plantilla.find("for(const am in LISTAS_ESCENA)")]
        for lid in sorted(set(re.findall(r"'([a-z]+)'", bloque))):
            if lid not in cat["listas"]:
                err_mu.append(f"Escena con una lista que no existe en el catálogo: {lid}")
        if err_mu:
            print("\nERRORES EN LA MÚSICA:"); print("\n".join(err_mu)); sys.exit(1)
        mu = {"licencia": cat["licencia"], "listas": cat["listas"],
              "pistas": {k: {"t": v["t"], "a": v["a"], "dur": v["dur"], "pagina": v["pagina"]} for k, v in cat["pistas"].items()}}
        salida = salida.replace(HUECO_MU, "const MUSICA = " + json.dumps(mu, ensure_ascii=False, separators=(",", ":")) + ";")
        minutos = sum(v["dur"] for v in cat["pistas"].values()) / 60
        print(f"\nMúsica: {len(cat['pistas'])} pistas en {len(cat['listas'])} listas ({minutos:.0f} minutos).")
    APP.write_text(salida, encoding="utf-8")
    total = sum(len(v) for v in cartas.values())
    print(f"\nInyectadas {total} cartas en {APP.name}.")


if __name__ == "__main__":
    main()

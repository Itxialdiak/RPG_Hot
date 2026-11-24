#!/usr/bin/env python3
"""Valida la escapada (escapada/base.json y las 12 combinaciones) y la prepara para inyectarla en la app.

Uso:  python3 build/escapada.py            -> valida lo que haya
      python3 build/escapada.py --completo -> exige las 12 combinaciones
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inyectar import GENERO, GENERO_OK, SUMISION, EXPLICITO  # mismos filtros que las cartas

ESTACIONES = ["primavera", "verano", "otono", "invierno"]
ALOJAMIENTOS = ["hotel", "furgo", "acampada"]
FASES_PROP = {"viaje": {"copi"}, "llegada": {"uno", "ambos"}, "explora": {"uno"}, "cena": {"uno", "ambos"}}
FASES_MAZO = {"perdidos", "alcoba"}
MINIMOS = {"viaje": 12, "llegada": 10, "explora": 16, "cena": 10, "perdidos": 8, "alcoba": 10}


def etiquetas_conocidas():
    src = (RAIZ / "build" / "plantilla.html").read_text(encoding="utf-8")
    bloque = src[src.find("const ETIQUETAS"):src.find("const SENALES")]
    return set(re.findall(r'\{id:"([a-z]+)", n:"', bloque))


def revisar_texto(origen, it, avisos):
    for campo in ("t", "x", "suave"):
        txt = it.get(campo) or ""
        for m in GENERO.finditer(txt):
            trozo = txt[max(0, m.start() - 14): m.end() + 14]
            if not any(ok.lower() in trozo.lower() for ok in GENERO_OK + ["la otra persona", "cada cual", "uno a uno", "una a una", "a solas", "desnuda a", "la lista", "lista de", "contra ella", "de ella", "en ella", "cada uno.", "cada una que", "rincón tranquilo", "oído atento", "ninguna tienda", "todas las luces", "esté lista"]):
                avisos.append(f"GÉNERO   {origen} {it['id']}.{campo}: «{m.group(0)}» … {trozo!r}")
        for m in SUMISION.finditer(txt):
            avisos.append(f"SUMISIÓN {origen} {it['id']}.{campo}: «{m.group(0)}»")
        for m in EXPLICITO.finditer(txt):
            avisos.append(f"EXPLÍCITO {origen} {it['id']}.{campo}: «{m.group(0)}»")
        m2 = re.search(r"(\{[RO]\}|tu pareja)\s+(enter|desnud|quiet|tumbad|sentad|dormid|vendad|atad)[oa]s?\b", txt)
        if m2:
            avisos.append(f"GÉNERO   {origen} {it['id']}.{campo}: adjetivo con género tras la persona: «{m2.group(0)}»")
        if re.search(r"\bapetec", txt):
            avisos.append(f"APETECE  {origen} {it['id']}.{campo}: la regla de la casa evita «¿te apetece?»")


def validar_item(origen, it, tags_ok, ids, errores, avisos):
    iid = it.get("id")
    if not iid:
        errores.append(f"{origen}: propuesta sin id"); return
    if iid in ids:
        errores.append(f"{origen}: id repetido {iid} (ya en {ids[iid]})")
    ids[iid] = origen
    f = it.get("f")
    for campo in ("t", "x"):
        if not (it.get(campo) or "").strip():
            errores.append(f"{origen} {iid}: falta «{campo}»")
    x = it.get("x", "")
    if f in FASES_PROP:
        if it.get("para") not in FASES_PROP[f]:
            errores.append(f"{origen} {iid}: «para» {it.get('para')!r} no vale en {f}")
        if "{R}" in x:
            errores.append(f"{origen} {iid}: {{R}} solo en los mazos")
        if it.get("para") == "ambos" and "{O}" in x:
            errores.append(f"{origen} {iid}: {{O}} en una propuesta para los dos")
        if f == "explora":
            if not (it.get("suave") or "").strip():
                errores.append(f"{origen} {iid}: reto sin versión suave")
            if not isinstance(it.get("min"), int) or not 20 <= it["min"] <= 70:
                errores.append(f"{origen} {iid}: «min» debe ir de 20 a 70")
            if it.get("nivel") not in (1, 2, 3, 4):
                errores.append(f"{origen} {iid}: reto sin nivel 1-4")
            if "{R}" in it.get("suave", ""):
                errores.append(f"{origen} {iid}: {{R}} en la versión suave")
    elif f in FASES_MAZO:
        if it.get("temp") not in ("seda", "brasa"):
            errores.append(f"{origen} {iid}: temperatura inválida")
        if "{O}" in x:
            errores.append(f"{origen} {iid}: en los mazos se usa {{R}}, no {{O}}")
    else:
        errores.append(f"{origen} {iid}: fase desconocida {f!r}")
    if "nivel" in it and it["nivel"] not in (1, 2, 3, 4):
        errores.append(f"{origen} {iid}: nivel fuera de 1-4")
    for t in it.get("tags", []):
        if t not in tags_ok:
            errores.append(f"{origen} {iid}: etiqueta desconocida «{t}»")
    if len(x) > 330:
        avisos.append(f"LARGA    {origen} {iid}: {len(x)} caracteres")
    if len(it.get("suave", "")) > 260:
        avisos.append(f"LARGA    {origen} {iid}.suave: {len(it['suave'])} caracteres")
    revisar_texto(origen, it, avisos)


def cargar(completo=False):
    tags_ok = etiquetas_conocidas()
    errores, avisos, ids = [], [], {}
    base = json.loads((RAIZ / "escapada" / "base.json").read_text(encoding="utf-8"))
    for it in base["propuestas"]:
        if it.get("est") and it["est"] not in ESTACIONES:
            errores.append(f"base {it['id']}: estación desconocida")
        if any(e not in ESTACIONES for e in it.get("noest", [])):
            errores.append(f"base {it['id']}: «noest» con estación desconocida")
        if it.get("alo") and it["alo"] not in ALOJAMIENTOS:
            errores.append(f"base {it['id']}: alojamiento desconocido")
        validar_item("base", it, tags_ok, ids, errores, avisos)
    combos, resumen = {}, []
    for est in ESTACIONES:
        for alo in ALOJAMIENTOS:
            p = RAIZ / "escapada" / f"{est}-{alo}.json"
            if not p.exists():
                if completo:
                    errores.append(f"falta la combinación {est}-{alo}")
                continue
            c = json.loads(p.read_text(encoding="utf-8"))
            origen = f"{est}-{alo}"
            for campo in ("titulo", "gancho", "lugar"):
                if not (c.get(campo) or "").strip():
                    errores.append(f"{origen}: falta «{campo}»")
            for k in ("perdidos", "alcoba"):
                carta = (c.get("cartas") or {}).get(k) or {}
                if not carta.get("parrafos"):
                    errores.append(f"{origen}: falta la carta de {k}")
            for it in c.get("propuestas", []):
                validar_item(origen, it, tags_ok, ids, errores, avisos)
            # piscinas compuestas: común + estación + alojamiento + combinación
            todas = [it for it in base["propuestas"] if (not it.get("est") or it["est"] == est) and (not it.get("alo") or it["alo"] == alo) and est not in it.get("noest", [])] + c.get("propuestas", [])
            tamaños = {}
            for f, minimo in MINIMOS.items():
                n = [it for it in todas if it["f"] == f]
                tamaños[f] = len(n)
                if len(n) < minimo:
                    errores.append(f"{origen}: {f} tiene {len(n)} (mínimo {minimo})")
                if f in FASES_MAZO:
                    for tmp in ("seda", "brasa"):
                        k = sum(1 for it in n if it.get("temp") == tmp)
                        if k < 4:
                            errores.append(f"{origen}: {f} tiene {k} cartas {tmp} (mínimo 4)")
            sin_aire = sum(1 for it in todas if it["f"] == "explora" and "aire" not in it.get("tags", []))
            if sin_aire < 8:
                errores.append(f"{origen}: solo {sin_aire} retos sin «Al aire libre» (si se veta, se quedan cortos)")
            resumen.append(f"{origen:22} " + " · ".join(f"{f} {n}" for f, n in tamaños.items()) + f" · retos sin aire {sin_aire}")
            combos[f"{est}/{alo}"] = c
    datos = dict(base)
    datos["combos"] = combos
    return datos, errores, avisos, resumen


if __name__ == "__main__":
    datos, errores, avisos, resumen = cargar("--completo" in sys.argv)
    print("\n".join(resumen) or "Sin combinaciones todavía.")
    if avisos:
        print("\nAvisos:"); print("\n".join(avisos))
    if errores:
        print("\nERRORES:"); print("\n".join(errores)); sys.exit(1)
    print(f"\nEscapada válida: {len(datos['propuestas'])} propuestas comunes y {len(datos['combos'])} combinaciones.")

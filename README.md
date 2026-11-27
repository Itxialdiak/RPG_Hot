# Doble Llave

Juegos de rol para dos, para encender una noche (o una tarde) poco a poco. Tres ambientaciones (*La última noche de Carnaval*, *El Bosque del Velo* y *La puerta de enfrente*), cada una con cuatro modos: **Con prohibiciones**, **Encender poco a poco**, **Sin rodeos** y **Con guion**. Cada escena trae su música, dentro de la app.

Y un juego aparte, **Una escapada de verdad**, para un viaje real: sin personajes, con propuestas que llegan solas desde que salís de casa hasta la alcoba. Está pensado para la app de Android, que avisa aunque el móvil esté bloqueado.

El mismo juego existe de cuatro formas, todas sacadas de los mismos datos:

| Forma | Dónde está | Para qué |
|---|---|---|
| Un solo archivo HTML | `doble-llave.html` | Abrirlo en cualquier navegador, sin instalar nada. |
| Web instalable (PWA) | `web/` | Publicarla en una URL; en Android se instala como una app y funciona sin conexión. |
| App de Android (APK) | `app-android/` | La misma web dentro de una app: botón Atrás, pantalla encendida mientras hay cartas, compartir nativo y los avisos de la escapada. |
| Cuadernos para imprimir | `salida/*.pdf` | Jugar sin pantallas: reglas, cartas recortables, sobres, fichas. Uno por ambientación con sus cuatro modos (unas 80 páginas: se imprime solo el que se vaya a jugar); la escapada no tiene versión impresa. |

## Los cuatro modos

| Modo | Cómo se juega |
|---|---|
| **Con prohibiciones** | Por turnos. Cada escena prohíbe algo; romperlo está permitido, pero cuesta una ficha, que se cobra al final como un favor. |
| **Encender poco a poco** | En cada turno una persona recibe y elige la temperatura, Seda o Brasa; la otra lee la carta en silencio. Pensado para el deseo que llega cuando ya se está disfrutando. |
| **Sin rodeos** | Por turnos, y el más explícito: las cartas llaman a las cosas por su nombre y sugieren más (también la penetración, siempre «si queréis» y al ritmo de quien recibe), sin palabras soeces, sin anatomía con género y sin instrucciones de dónde ni cómo. Cada escena pone una condición en vez de una prohibición (la ropa que cae no vuelve) y las fichas sirven para pedir más. |
| **Con guion** | Más rol que cartas. Cada escena trae una situación, un papel secreto para cada persona (qué quiere su personaje, qué sabe y qué esconde) y un mazo de giros que empujan la historia y la temperatura. Los papeles se reparten al azar al empezar y se mantienen toda la noche; la historia es la misma de la ambientación, contada desde dentro: en Carnaval, una noche que quedó a medias hace un año; en el Bosque, un trato con las hadas que vence esta noche; en la tarde de lluvia, unas llaves que nunca se perdieron. |

En los tres modos con cartas, cada escena con mazo trae además dos **giros de la historia** («Un giro de la historia»): algo que pasa y un gesto para jugarlo en personaje. Son opcionales: quien quiera ir solo a las cartas, los deja pasar.

Los NO tienen tres etiquetas nuevas, **Juguetes**, **Tocarse** y **Al borde**, que solo aparecen si alguna carta de la partida las usa. Si lo marcado deja una escena con menos de tres cartas (la Venda en la tercera escena, o Desnudez y Zonas íntimas en Sin rodeos), la app lo avisa antes de empezar.

## La puerta de enfrente

La ambientación cotidiana: una tarde, no una noche, y en vuestra casa tal como es. Un sábado de lluvia, alguien del rellano se queda sin llaves y llama a la puerta de enfrente; la cerrajería no llega hasta las siete. Se juega con papeles (no sois vosotros, sino gente del edificio: «la bici del portal», «el turno de noche»…), sin disfraces ni nada raro: una toalla, café, una manta, una vela para el apagón. Escribe las cartas «el edificio».

| | Con prohibiciones | Encender poco a poco | Sin rodeos | Con guion |
|---|---|---|---|---|
| El rellano | No os toquéis | La mirada y la palabra | Solo se habla, y claro | No os toquéis |
| I | La cocina | La cocina | La entrada | La cocina |
| II | El salón | El baño | El sofá | El salón |
| III | El apagón | El apagón | La ducha | El apagón |
| IV | El dormitorio | El dormitorio | El dormitorio | El dormitorio |

Las fichas son Favores (con prohibiciones y con guion), Antojos (encender) y Vales (sin rodeos); el oráculo, «las notas de la nevera». Tiene su cuaderno para imprimir, como las otras dos.

## La música

Cada escena suena con una o dos listas elegidas para ella (barroco y clavecín en Venecia, arpa y folk en el Bosque, radio de cocina, soul lento y jazz de madrugada en la tarde de lluvia…): 55 pistas de **Kevin MacLeod** ([incompetech.com](https://incompetech.com)), con licencia [Creative Commons Atribución 4.0](https://creativecommons.org/licenses/by/4.0/). Los créditos de cada pista están en la app: Ayuda → Créditos de la música.

- Antes de empezar se elige con música o sin ella, y se puede pausar o saltar en cualquier momento. «Rojo» la para.
- Las escenas con cartas duran lo que su música: cuando se cumple el tiempo de la escena, la música termina al acabar la canción que suena. Las cartas que dicen «durante una canción» tienen un botón para empezar una desde el principio.
- La lista está en `musica/catalogo.json`. Los archivos no van en el repositorio: `node herramientas/musica.mjs` los descarga de incompetech.com una sola vez, iguala el volumen y los comprime a Opus (unos 65 MB en total) en `musica/salida/`. Necesita ffmpeg. Los flujos de GitHub Actions lo hacen solos y lo guardan en caché.
- La APK lleva la música dentro y funciona sin conexión. La web instalable la carga de la red (sin conexión, sin música). El HTML suelto no la lleva: cada escena sigue diciendo qué tipo de música poner, igual que el PDF.

## La escapada

Se elige la estación (primavera, verano, otoño o invierno) y dónde se duerme (hotel u hostal en un pueblo, furgoneta camperizada o acampada): 12 combinaciones, cada una con sus propuestas, sus cartas para perderse (12 o 13) y su alcoba (16 o 17). Las propuestas se componen por capas: comunes, de la estación, del alojamiento y de la combinación.

El juego va por fases, y sois vosotros quienes marcáis en cuál estáis:

| Fase | Qué pasa |
|---|---|
| El viaje | Propuestas tranquilas, cada 20 a 35 minutos. Las lee en voz alta quien no conduce; si nadie conduce (tren, autobús), por turnos. |
| La llegada | Más a menudo y un poco más subidas. Son personales: llegan casi a la vez una «Para Alex» y otra «Para Sam», o una para compartir, y cada cual mira solo la suya. |
| Explorar (opcional) | Cada persona tiene un reto secreto con cuenta atrás. Si se cumple, si caduca, o si la pareja pide algo más suave o dice que no, llega otro. Lo rechazado no vuelve y el tono baja; lo cumplido lo sube. |
| Perdidos (opcional) | Desde Explorar: el mazo al aire libre (Seda o Brasa), con el tono al máximo y solo a solas de verdad. Tiene botón «Viene alguien». Al terminar, la tarde sigue en modo cena. |
| La cena (opcional) | Un respiro, con el ambiente encendido y propuestas más espaciadas. |
| La alcoba | La carta del sitio, las cartas que escribisteis antes de salir, el oráculo si queréis y el mazo de la alcoba. |

Con «Fases» se puede saltar a cualquiera, también hacia atrás: para el día siguiente o para el viaje de vuelta. «Pausa» detiene las propuestas media hora, una hora o hasta quitarla, y «Rojo» las pausa siempre. Si vetáis «Al aire libre», desaparecen Perdidos y los retos de fuera.

### Los avisos

- En la APK, cada propuesta y cada reto llegan como un aviso del sistema, también con el móvil bloqueado. El aviso nunca dice qué es: solo «Doble Llave» y «Algo para Sam», «Algo para compartir» o «Un reto nuevo para Alex». El canal va en modo privado en la pantalla de bloqueo.
- Los avisos son inexactos a propósito: Android puede retrasarlos unos minutos para ahorrar batería, y así la app no necesita el permiso de alarmas exactas. Si en vuestro móvil no llegan, quitad la app de la optimización de batería: en los ajustes del móvil, en la batería de Doble Llave, elegid «Sin restricciones». Algunas marcas son muy agresivas con esto.
- Entre la una y las siete de la mañana no se programa nada.
- En el navegador (el HTML o la web instalable) no hay avisos: lo que haya llegado aparece al abrir la página.
- La pantalla solo se mantiene encendida con las cartas (Perdidos y la alcoba). El resto del viaje, el móvil duerme y avisa.

## Guardado

Todo se queda en el dispositivo, nunca en internet:

- **La noche preparada** (modo, ambientación, lista, invitación) se guarda hasta que la borréis.
- **La partida en curso** se guarda mientras dura, para seguir si se cierra la app, se apaga la pantalla o se recarga la página. En el inicio aparece «Partida a medias → Seguir la partida». Al terminar o salir de la partida, se borra.
- **La escapada en curso** se guarda hasta cinco días y, al abrir la app (o tocar un aviso), aparece directamente en su fase.
- Lo que cada persona marca en secreto en el Oráculo o el Pozo **no se guarda nunca**, ni siquiera durante la partida.

Si abrís el HTML directamente como archivo en el móvil, algunos navegadores no guardan nada. Desde una web (la PWA) o desde la APK, sí.

## La APK de Android

### Opción A: en la nube, sin instalar nada (recomendada)

1. Subid esta carpeta a un repositorio de GitHub. Si es privado, el enlace de Releases solo funciona con vuestra sesión iniciada.
2. Pestaña **Actions → APK de Android → Run workflow**.
3. Al terminar (unos 5 minutos; la primera vez algo más, porque descarga la música), la APK queda publicada en **Releases** con un enlace fijo que se puede abrir directamente en el móvil, sin cuenta de GitHub y sin zip: `https://github.com/<usuario>/<repositorio>/releases/download/apk/doble-llave.apk` (unos 80 MB con la música). También está como artefacto `doble-llave-apk` en la ejecución de Actions, dentro de un zip.
4. En el móvil, abrid el archivo y permitid «instalar aplicaciones de origen desconocido» para esa app.

Cada vez que cambie `doble-llave.html`, `app-android/` o la música, la APK se vuelve a compilar sola. Todas salen firmadas con la misma clave de depuración del proyecto (`app-android/android/app/debug.keystore`, contraseña pública `android`), así que una APK nueva se instala encima de la anterior sin perder lo guardado.

### Opción B: en vuestro ordenador

Hace falta Node 22, JDK 21 y Android Studio.

```bash
cd app-android
npm install
node ../herramientas/musica.mjs   # opcional: descarga y prepara la música (necesita ffmpeg)
npm run sync        # copia doble-llave.html (y la música, si está) dentro de la app
npm run abrir       # abre Android Studio; desde ahí, Run o Build → Build APK
```

### Antes de publicarla en una tienda

- Cambiad el identificador `com.doblellave.app` (en `capacitor.config.json` y `android/app/build.gradle`) por uno de un dominio vuestro.
- Cread una clave de release propia y no la subáis al repositorio.
- Ojo: Google Play no admite apps con contenido sexual, y un juego erótico para parejas tiene muchas papeletas de ser rechazado. Para uso propio, instalar la APK directamente no tiene ese problema.
- La app pide permiso para mostrar avisos (Android 13 o posterior) la primera vez que empieza una escapada, o antes, desde «Antes de salir».

## La web instalable

`web/` está lista para publicar en cualquier alojamiento estático (GitHub Pages, Netlify, Cloudflare Pages…). Con GitHub: **Settings → Pages → Source: GitHub Actions** y el flujo «Web instalable» la publica en cada cambio (la primera vez, lanzadlo a mano desde Actions). Mientras Pages no esté activado, el flujo termina sin publicar nada. Ojo: si el repositorio es público, la web también lo es; GitHub Pages en repositorios privados necesita un plan de pago.

En Android, abrid la URL en Chrome → menú → **Instalar aplicación**. En iPhone, Safari → Compartir → **Añadir a pantalla de inicio**. Desde la web, la preparación de cada noche ofrece también su PDF para imprimir.

## Cambiar o añadir cartas

Las cartas están en `cartas/<ambientación>-<modo>.json`, una por línea, y los giros de la historia en `cartas/<ambientación>-giros.json`. Las cartas que se leen en voz alta, los papeles de Con guion, los Secretos y el oráculo están en `build/plantilla.html`. Las de la escapada, en `escapada/`: `base.json` (lo común, lo de cada estación y lo de cada alojamiento, más las fases, la seguridad y el material) y un archivo por combinación, `<estación>-<alojamiento>.json`, con su título, sus consejos, sus cartas de Perdidos y de la alcoba y sus propuestas. `python3 build/escapada.py --completo` las valida por separado: tamaños por fase, equilibrio Seda/Brasa, versión suave de cada reto, retos de sobra sin «Al aire libre» y los mismos avisos de lenguaje que las cartas.

Después de tocarlas:

```bash
python3 build/inyectar.py              # valida las cartas y regenera doble-llave.html
node herramientas/construir-web.mjs    # regenera web/
cd app-android && npm run sync         # actualiza la app
```

`inyectar.py` comprueba el número de cartas por escena, el equilibrio Seda/Brasa, las etiquetas de los NO y avisa de lenguaje con género, de dominación o más explícito de lo que permite cada modo (Sin rodeos admite más vocabulario, pero no palabras soeces ni anatomía con género). Lo que no detecta una expresión regular, como una carta que dé instrucciones de dónde o cómo, se revisa a mano. Cada carta lleva sus etiquetas (Desnudez, Zonas íntimas, Ataduras…): si una carta pide algo, tiene que llevar su etiqueta, porque es lo que permite vetarla.

Para regenerar los PDF hace falta Python con Playwright y Chrome o Chromium:

```bash
cd print && npm install && cd ..       # tipografías (Cormorant Garamond, IM Fell English y Fraunces, licencia OFL)
python3 print/generar.py               # escribe salida/*.pdf (o: python3 print/generar.py cotidiana)
```

Los iconos y las pantallas de arranque se generan con `python3 herramientas/iconos.py`.

## Estructura

```
doble-llave.html         el juego, en un solo archivo (se genera; no editar a mano)
build/plantilla.html     el motor y los textos del juego, con el hueco donde van las cartas
build/inyectar.py        valida las cartas y la escapada y genera doble-llave.html
build/escapada.py        valida la escapada
cartas/                  las cartas de cada ambientación y modo, y los giros de la historia
escapada/                la escapada: lo común y las 12 combinaciones
musica/catalogo.json     la música de cada escena (Kevin MacLeod, CC BY 4.0)
print/                   generador de los PDF para imprimir
salida/                  los PDF
web/                     la versión web instalable (se genera)
app-android/             el proyecto de Android (Capacitor 8)
herramientas/            iconos, construcción de la web y descarga de la música
.github/workflows/       compilación de la APK y publicación de la web
```

<!-- ¿Será que alguien está midiendo eso? — versión en español (es).
     Fuente y convenciones: slides.en.md + README.md. Traducción fiel: la estructura HTML,
     las rutas de imágenes y el código se mantienen idénticos al inglés.
     IMAGE-FIRST: las diapositivas son imágenes + un texto mínimo. La charla vive en los
     bloques Note: (presiona S para la vista del presentador). Mantén el texto en pantalla
     mínimo y no literal. -->
<!-- .slide: class="divider title-slide" data-background-color="var(--dark)" -->

# ¿Será que alguien está<br><span class="hl">midiendo eso?</span>

<p class="byline">David Eads &nbsp;·&nbsp; davideads@gmail.com<br>recoveredfactory.net</p>

Note:
Soy periodista de datos —lo que básicamente significa que soy un ingeniero full-stack cuyo producto final son noticias o investigaciones—. Hoy, ustedes también van a serlo.

Es chévere porque puedes usar la ciencia, la lógica y la tecnología para, ojalá, hacer del mundo un lugar un poco más justo y humano. Y también simplemente por curiosidad: para detenerte, ver el mundo de otras maneras y hablar con gente interesante. No me ha hecho rico, pero he conocido el mundo y he podido ver la historia mientras sucede.

---

<!-- .slide: class="bleed" data-background-image="assets/mexico-graves-map.png" data-background-size="cover" data-background-color="var(--dark)" -->

Note:
Mucho de lo que he hecho —y sigo haciendo— trata sobre temas pesados. Derechos humanos, discriminación, los desaparecidos. Este es un mapa de fosas clandestinas en México. Volveremos a este proyecto en particular al final de la charla, una vez que hayamos hablado del proceso.

Pero también hago esto por diversión, por placer, por mi propia curiosidad y mi sentido de la belleza. Vamos a empezar con ejemplos de ese tipo, cosas que te podrías imaginar haciendo para hacerte la vida un poco mejor o más fácil.

---

<!-- .slide: class="divider steps" data-background-color="var(--dark)" -->

<p class="eyebrow">El proceso</p>

<p>(<b>Paso 0</b>: Haz una buena pregunta.)</p>

<ol class="steps-list">
<li>Adquisición de datos</li>
<li>Procesamiento</li>
<li>Análisis y visualización</li>
<li>Reportería</li>
<li>Publicación</li>
</ol>

Note:
Todo proyecto empieza con una pregunta de dos partes. La primera es algo como: ¿las multas de tránsito llevan a la gente a la quiebra? ¿Qué barrios tienen más contenedores de basura?

La segunda parte es: ¿alguien midió eso?

Si la respuesta es sí, entonces necesitas conseguir los datos, limpiarlos hasta tener algo con qué trabajar, encontrar qué significan y mostrarlo, escribirlo, y sacarlo al mundo.

---

<!-- .slide: class="bleed" data-background-image="assets/lake-summer.jpg" data-background-size="cover" data-background-color="var(--dark)" -->

<h2 class="overlay-q">¿El agua está suficientemente tibia para nadar?</h2>

Note:
Empecemos con un proyecto alegre. La pregunta era esta: ¿hace suficiente calor para ir a nadar?

Yo vivía en Chicago, junto a un lago enorme —básicamente un mar—. Me encantaba salir a trotar y luego lanzarme al agua cuando vivía cerca de una de las playas.

---

<!-- .slide: class="bleed" data-background-image="assets/lake-frozen.jpg" data-background-size="cover" data-background-color="var(--dark)" -->

<p class="photo-credit">"Frozen Staircase to Lake Michigan" — <a href="https://flickr.com/photos/shutterrunner/32404337645/">Shutter Runner / Flickr</a> · CC BY-NC 2.0</p>

Note:
El problema: Chicago es frío la mayor parte del año. Esta no es mi foto, pero es de la misma playa, solo que mirando hacia el otro lado. Y en pleno invierno. Así que quería saber: ¿cuándo está el lago suficientemente tibio, para lo que yo tolero, como para ir a nadar?

---

<!-- .slide: class="step" -->

<figure>
  <img src="assets/seagull.png" alt="API de sensores Seagull">
  <figcaption class="step"><span class="n">1.</span> Adquirir</figcaption>
</figure>

Note:
De nuevo: ¿me pregunto si alguien estará midiendo eso? En este caso supuse que debía haber sensores en el lago midiendo temperatura y viento. Buena parte del monitoreo ambiental en Estados Unidos es público, así que pensé que quizá tenía alguna posibilidad de encontrar algo. Milagrosamente, unas pocas búsquedas después, ¡descubrí que sí! Una universidad acababa de publicar una API para cada sensor de toda la región de los Grandes Lagos. Se llama Seagull.

Hay todo tipo de datos por ahí esperando a que los liberen. ¿Cuántos niños se lastiman en camas elásticas? Una agencia en Estados Unidos lleva esa cuenta. Y especialmente en México y Colombia hay ahora *más* datos públicos interesantes que en Estados Unidos —solo que están encerrados en sistemas viejos y peculiares—.

---

<!-- .slide: class="step" -->
<!-- CODE SLIDES: use a BARE top-level <pre> (NOT wrapped in <figure>) so blank lines are
     allowed — marked treats <pre> as a type-1 HTML block (blank-line-safe); a <figure>
     wrapper is type-6 and ENDS at the first blank line, re-parsing the rest as Markdown
     (# → <h1>, URLs autolink). The "N. Verb" label is a standalone <figcaption>. -->

<pre><code class="language-python" data-trim data-line-numbers>import datetime as dt, requests, pandas as pd
etiquetas = {20: "Temperatura del agua", 21: "Viento"}
hoy = dt.date.today()

consulta = {
    "startDate": (hoy - dt.timedelta(days=7)).isoformat(),
    "endDate": hoy.isoformat(),
    "obsDatasetId": 98,
    "parameterId": ",".join(map(str, etiquetas)),
}
res = requests.get("https://seagull-api.glos.org/api/v1/obs",
                   params=consulta).json()

# aplanar el JSON anidado en una sola tabla ordenada
filas = [{**obs, "parametro": etiquetas[p["parameter_id"]]}
         for p in res[0]["parameters"] for obs in p["observations"]]
df = pd.DataFrame(filas)
df["fecha"] = pd.to_datetime(df["timestamp"])
</code></pre>

<figcaption class="step"><span class="n">2.</span> Procesar</figcaption>

Note:
Procesamiento. Armé una consulta para unos días recientes, traje el JSON y aplané su forma anidada en una sola tabla ordenada que pudiera analizar. Sin base de datos, sin archivo —hazlo simple—. (Esto nació como un cuaderno de Observable en JavaScript; aquí está la misma idea en Python.)

---

<!-- .slide: class="step" -->

<pre><code class="language-python" data-trim data-line-numbers># solo la temperatura del agua, promedio diario
agua = (df[df.parametro == "Temperatura del agua"]
        .set_index("fecha")["value"].resample("D").mean())

# "escala sentida": clasificar la temperatura en bandas cualitativas
bordes = [-99, 12, 14, 16, 18, 22, 24, 99]
nombres = ["peligroso", "vigorizante", "terapéutico", "tolerable",
           "nadable", "🤩 perfecto", "muy cálido :/"]
sensacion = pd.cut(agua, bins=bordes, labels=nombres)

print("hoy el lago se siente:", sensacion.iloc[-1])
sensacion.value_counts()   # cuántos días en cada sensación
</code></pre>

<figcaption class="step"><span class="n">3.</span> Analizar</figcaption>

Note:
Analizar es decidir qué *significan* los números. No tengo intuición para 14 °C frente a 20 °C, así que busqué qué consideran peligroso los científicos —ese fue mi piso—. Después, cada vez que nadaba, anotaba la temperatura y cómo se sentía de verdad. Con suficientes registros, pude proyectar esa experiencia de vuelta sobre los datos —una "escala sentida" que convierte un número en una sensación—. `pd.cut` hace exactamente eso: corta la temperatura continua en mis bandas con nombre. 22 °C se siente perfecto después de un trote duro.

Los números son una señal —pero es mi experiencia combinada con ellos lo que les da sentido—.

El lago a veces supera ahora los 24 °C, que también se siente genial, pero es más alto que cualquier temperatura registrada antes. Incluso en este proyecto divertido, un pequeño recordatorio del cambio climático.

---

<!-- .slide: class="step" -->

<figure>
  <img class="tall" src="assets/waves-charts-mejor.png" alt="Gráfica de temperatura del lago con bandas de sensación">
  <figcaption class="step"><span class="n">4.</span> Visualizar + publicar</figcaption>
</figure>

Note:
No puedes analizar sin visualizar. Esta gráfica y estas frases proyectan mis opiniones y mi experiencia de las condiciones del lago sobre los datos, y luego los presentan de una forma que profundiza nuestra comprensión: la gráfica de líneas nos muestra no solo la temperatura actual, sino la tendencia.

No hice mucha reportería para esto, aunque sí llamé y hablé con las personas que hacen la API para asegurarme de estar usando el sistema correctamente y con los números correctos. Y publiqué mi trabajo en un cuaderno público.

---

<div class="phones">
  <figure><img class="phone" src="assets/cali-mobile-trees.png" alt="Mapas Cali — mapa de calor de densidad de árboles (móvil)"></figure>
  <figure><img class="phone" src="assets/cali-mobile-traffic-level-of-service.png" alt="Mapas Cali — nivel de servicio del tráfico (móvil)"></figure>
</div>

<p class="site-url">cali.recoveredfactory.net</p>

Note:
Ahora de Chicago a Cali. Hace unos años me enamoré de alguien de aquí —y de la ciudad: la cultura, las montañas, el clima, la energía—. Así que, por supuesto, quise ver qué datos podía encontrar sobre ella. Después de escarbar, encontré un servidor de mapas difícil de manejar pero lleno de datos fascinantes —la ciudad en realidad publica muchísimo—. Esto fue en 2024, antes de que la IA se volviera buena con el código: escribí un scraper primitivo, vi que era una mina de oro —densidad de árboles, un modelo digital de elevación, la ciudad en 3D— y lo dejé a un lado porque era mucho trabajo decodificar el sistema. En este sentido, la IA ha sido increíble. Hacerle scraping a un sistema así antes era demasiado para la mayoría de los principiantes. Cuando volví a retomarlo, simplemente le pedí a Claude que trajera cada dataset que la ciudad publica y lo procesara para mapas web —pero todavía necesitaba el modelo mental: cómo encaja todo el sistema y qué herramientas usar—.

---

<p class="eyebrow">Los pilares</p>

<ul class="stack">
  <li><b>Dagster</b> — basado en Python; "orquesta" pipelines de datos para procesarlos.</li>
  <li><b>Protomaps</b> — procesa y convierte los datos para sistemas modernos.</li>
  <li><b>SvelteKit con MapLibre</b> — SvelteKit ofrece un frontend sencillo (hay muchas opciones); MapLibre es hoy la mejor librería abierta de mapas web.</li>
  <li><b>AWS + SST</b> — despliegue.</li>
</ul>

Note:
Estos son los cuatro pilares de la construcción de Cali —la respuesta a "qué herramientas usar"—. Dagster orquesta el pipeline en Python: adquirir, luego procesar. Protomaps convierte cientos de capas en un único formato de tiles moderno y eficiente. MapLibre dibuja el mapa en el navegador, con SvelteKit como un frontend liviano a su alrededor. AWS, conectado con SST, lo pone en línea.

---

<!-- .slide: class="step" -->

<figure>
  <img src="assets/idesc-page.png" alt="Geoportal IDESC — catálogo de datos espaciales de Cali">
  <figcaption class="step"><span class="n">1.</span> Adquirir</figcaption>
</figure>

Note:
Paso uno, adquirir. Esto es IDESC —el catálogo abierto de datos espaciales de Cali—. Todo lo que la ciudad publica vive aquí: servicios WFS y WMS, descargas, ortoimágenes, un geocodificador. Adquirir es simplemente meter esa materia prima por la puerta —bajar cada capa para que el resto del pipeline tenga sobre qué construir—.

---

<!-- .slide: class="step" -->

<figure>
  <img src="assets/dagster-cali-map.png" alt="Dagster — linaje global de assets del pipeline del mapa de Cali">
  <figcaption class="step"><span class="n">2.</span> Procesar</figcaption>
</figure>

Note:
¿Por qué orquestar un pipeline? A esta escala —más de 350 capas, 6,6 GB de entrada— necesitas reconstruir tu resultado desde cero o parcialmente, probar su exactitud y agregar nuevas fuentes sin romper todo. Eso es lo que te da un orquestador.

---

<p class="eyebrow">Dagster · pasar datos entre assets</p>

<pre><code class="language-python" data-trim data-line-numbers>import dagster as dg

@dg.asset
def layer_geojson():                         # 1. adquirir
    raw = download("cali:buildings")         #    una capa del servidor WFS
    return reproject(raw, to="EPSG:4326")    #    → lat/lon estándar

@dg.asset                              # nombra el argumento como el asset de arriba…
def layer_pmtiles(layer_geojson):      # …y Dagster te entrega su salida
    return to_pmtiles(layer_geojson)         # 2. procesar → tiles de mapa
</code></pre>

Note:
Si escribes Python, Dagster es una gran opción. Es *data-first* (los datos primero): cada paso es un asset —un sustantivo, la cosa que quieres que exista—. Estos son los assets reales del pipeline del mapa de Cali, recortados. Aquí está la jugada clave: `layer_geojson` devuelve sus datos, y el siguiente asset simplemente recibe un argumento con ese mismo nombre —`def layer_pmtiles(layer_geojson)`—. Dagster conecta los dos y le entrega la salida del primer asset directamente al segundo. Los datos fluyen de un asset al siguiente; no andas haciendo malabares con archivos ni con variables globales. (Si un paso solo necesita correr *después* de otro pero no usa sus datos, escribirías `deps=[...]` en su lugar.)

Dos alternativas que vale la pena conocer: Prefect convierte Python existente en pipelines rápidamente, con menos estructura —bueno cuando tu trabajo es más verbos que sustantivos ("avísame")—. Airflow es maduro pero doloroso, sobre todo en grandes empresas y universidades.

---

<figure>
  <img src="assets/cali-3d.png" alt="Mapas Cali — vista de edificios en 3D de la ciudad">
  <figcaption>354 capas de Cali</figcaption>
</figure>

Note:
El resultado: 354 capas de mapa sobre Cali —árboles, ciclorrutas, zonas de inundación, tantísimo—. Parte es vieja y probablemente imprecisa, pero es increíble. Para el motor del mapa elegí Protomaps más MapLibre: casi tan potente como Mapbox, gratis y rápido en celulares económicos —algo que importa muchísimo en Colombia—. La IA escribió el código; yo elegí las herramientas. El siguiente paso es investigar y hacer llamadas para entender qué significan de verdad los datos.

Un mapa de clínicas, o de zonas con poco desarrollo, es inherentemente un mapa sobre justicia y política —lo que nos devuelve al trabajo pesado—.

---

<!-- .slide: class="bleed" data-background-image="assets/desaparecidos-map.png" data-background-size="cover" data-background-color="var(--dark)" -->

<h2 class="map-claim">El gobierno dijo: 230 fosas.<br>Nosotros contamos: casi 2.000.</h2>

Note:
En 2017–2018 fui parte de un equipo de periodistas mexicanos que ganó el Premio Gabo por nuestro trabajo sobre las fosas clandestinas y los desaparecidos. Construí un mapa que vieron millones de personas.

Lo que lo hizo buen periodismo de datos fue la curiosidad dirigida a la rendición de cuentas. El gobierno nacional decía que se habían encontrado unas 230 fosas. Pero las autoridades municipales y estatales también llevaban registro de fosas. Solicitamos esos registros, los sumamos —y contamos casi 2.000—. Se convirtió en un símbolo de la corrupción del gobierno.

Algo de lo que no hemos hablado todavía es que hay muchos tipos de datos: están los datos de medición, los datos de encuesta y los datos administrativos. Todos son interesantes, pero los datos administrativos suelen ser poderosos para la rendición de cuentas, porque puedes contrastar afirmaciones con el registro burocrático, o mirar lo que las instituciones poderosas _no_ registran.

---

<!-- .slide: class="bleed" data-background-image="assets/fosas-2023.png" data-background-size="cover" data-background-color="var(--dark)" -->

<h2 class="map-claim">En 2023, el gobierno finalmente reconoció más de 5.600 fosas.</h2>

Note:
Y el número nunca dejó de subir. Para 2023, el propio organismo de búsqueda del gobierno —la Comisión Nacional de Búsqueda— había reconocido más de 5.600 fosas clandestinas. La cifra por la que alguna vez nos pusieron en duda hoy queda pequeña frente al propio conteo del Estado. Esa es la recompensa de la curiosidad dirigida a la rendición de cuentas: con el tiempo, se reivindica.

---

<div class="phones grouped">
  <figure><img class="phone" src="assets/tcr-police-protest.png" alt="The Chicago Reporter — arrestos por protesta frente a saqueo"></figure>
  <div class="phone-group">
    <figure><img class="phone" src="assets/tmp-police-labor-01.png" alt="The Marshall Project — empleo policial"></figure>
    <figure><img class="phone" src="assets/tmp-police-labor-02.png" alt="The Marshall Project — empleo policial"></figure>
  </div>
</div>

<p class="eyebrow center">Eso lo puedo verificar</p>

Note:
El corazón de todo esto: alguien con poder dice "la contratación de policías se está desplomando", o "la mayoría de las personas que arrestamos estaban saqueando" —y tú piensas: *eso lo puedo verificar*—. En Chicago, la policía arrestó a más personas por protestar que por saquear. A nivel nacional, los oficiales decían que renunciaban en masa; los datos laborales decían que no.

---

<!-- .slide: class="quote" -->

<p class="q">"Me pregunto si alguien estará <span class="hl">midiendo eso."</span></p>

<p class="byline">Después, ve y verifícalo.<br>David Eads · davideads@gmail.com · recoveredfactory.net</p>

Note:
Esa es toda la charla en una sola línea: haz la pregunta y luego ve a verificar. Gracias.

Enlaces: observablehq.com/@eads/waves-on-my-beach · data.adondevanlosdesaparecidos.org

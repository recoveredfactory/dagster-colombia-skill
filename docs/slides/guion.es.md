# Guión del presentador — *Usar Python (y más) para explorar nuestro mundo*

> Solo las **notas del presentador** de la charla, extraídas de
> [`slides.es.md`](slides.es.md) (los bloques `Note:`). Es lo que se dice en voz alta;
> el texto en pantalla es mínimo y vive en las diapositivas. Para la vista del
> presentador con estas notas al lado, abre el deck y presiona **S**.
>
> Orden idéntico al de las diapositivas. Si editas el deck, vuelve a generar este guión.

---

## 1 · Apertura — periodismo de datos

Soy periodista de datos —lo que básicamente significa que soy un ingeniero full-stack cuyo producto final son noticias o investigaciones—. Hoy, ustedes también van a serlo.

Es chévere porque puedes usar la ciencia, la lógica y la tecnología para, ojalá, hacer del mundo un lugar un poco más justo y humano. Y también simplemente por curiosidad: para detenerte, ver el mundo de otras maneras y hablar con gente interesante. No me ha hecho rico, pero he conocido el mundo y he podido ver la historia mientras sucede.

## 2 · Por qué: temas pesados y curiosidad

Mucho de lo que he hecho —y sigo haciendo— trata sobre temas pesados. Derechos humanos, discriminación, los desaparecidos. Este es un mapa de fosas clandestinas en México. Volveremos a este proyecto en particular al final de la charla, una vez que hayamos hablado del proceso.

Pero también hago esto por diversión, por placer, por mi propia curiosidad y mi sentido de la belleza. Vamos a empezar con ejemplos de ese tipo, cosas que te podrías imaginar haciendo para hacerte la vida un poco mejor o más fácil.

## 3 · El proceso en cinco pasos

Todo proyecto empieza con una pregunta de dos partes. La primera es algo como: ¿las multas de tránsito llevan a la gente a la quiebra? ¿Qué barrios tienen más contenedores de basura?

La segunda parte es: ¿alguien midió eso?

Si la respuesta es sí, entonces necesitas conseguir los datos, limpiarlos hasta tener algo con qué trabajar, encontrar qué significan y mostrarlo, escribirlo, y sacarlo al mundo.

## 4 · Un proyecto alegre: ¿está el lago para nadar?

Empecemos con un proyecto alegre. La pregunta era esta: ¿hace suficiente calor para ir a nadar?

Yo vivía en Chicago, junto a un lago enorme —básicamente un mar—. Me encantaba salir a trotar y luego lanzarme al agua cuando vivía cerca de una de las playas.

## 5 · El problema: Chicago es frío

El problema: Chicago es frío la mayor parte del año. Esta no es mi foto, pero es de la misma playa, solo que mirando hacia el otro lado. Y en pleno invierno. Así que quería saber: ¿cuándo está el lago suficientemente tibio, para lo que yo tolero, como para ir a nadar?

## 6 · Paso 1 · Adquirir: la API Seagull

De nuevo: ¿me pregunto si alguien estará midiendo eso? En este caso supuse que debía haber sensores en el lago midiendo temperatura y viento. Buena parte del monitoreo ambiental en Estados Unidos es público, así que pensé que quizá tenía alguna posibilidad de encontrar algo. Milagrosamente, unas pocas búsquedas después, ¡descubrí que sí! Una universidad acababa de publicar una API para cada sensor de toda la región de los Grandes Lagos. Se llama Seagull.

Hay todo tipo de datos por ahí esperando a que los liberen. ¿Cuántos niños se lastiman en camas elásticas? Una agencia en Estados Unidos lleva esa cuenta. Y especialmente en México y Colombia hay ahora *más* datos públicos interesantes que en Estados Unidos —solo que están encerrados en sistemas viejos y peculiares—.

## 7 · Paso 2 · Procesar: traer y aplanar el JSON

Procesamiento. Armé una consulta para unos días recientes, traje el JSON y aplané su forma anidada en una sola tabla ordenada que pudiera analizar. Sin base de datos, sin archivo —hazlo simple—. (Esto nació como un cuaderno de Observable en JavaScript; aquí está la misma idea en Python.)

## 8 · Paso 3 · Analizar: la "escala sentida"

Analizar es decidir qué *significan* los números. No tengo intuición para 14 °C frente a 20 °C, así que busqué qué consideran peligroso los científicos —ese fue mi piso—. Después, cada vez que nadaba, anotaba la temperatura y cómo se sentía de verdad. Con suficientes registros, pude proyectar esa experiencia de vuelta sobre los datos —una "escala sentida" que convierte un número en una sensación—. `pd.cut` hace exactamente eso: corta la temperatura continua en mis bandas con nombre. 22 °C se siente perfecto después de un trote duro.

Los números son una señal —pero es mi experiencia combinada con ellos lo que les da sentido—.

El lago a veces supera ahora los 24 °C, que también se siente genial, pero es más alto que cualquier temperatura registrada antes. Incluso en este proyecto divertido, un pequeño recordatorio del cambio climático.

## 9 · Paso 4 · Visualizar + publicar

No puedes analizar sin visualizar. Esta gráfica y estas frases proyectan mis opiniones y mi experiencia de las condiciones del lago sobre los datos, y luego los presentan de una forma que profundiza nuestra comprensión: la gráfica de líneas nos muestra no solo la temperatura actual, sino la tendencia.

No hice mucha reportería para esto, aunque sí llamé y hablé con las personas que hacen la API para asegurarme de estar usando el sistema correctamente y con los números correctos. Y publiqué mi trabajo en un cuaderno público.

## 10 · De Chicago a Cali

Ahora de Chicago a Cali. Hace unos años me enamoré de alguien de aquí —y de la ciudad: la cultura, las montañas, el clima, la energía—. Así que, por supuesto, quise ver qué datos podía encontrar sobre ella. Después de escarbar, encontré un servidor de mapas difícil de manejar pero lleno de datos fascinantes —la ciudad en realidad publica muchísimo—. Esto fue en 2024, antes de que la IA se volviera buena con el código: escribí un scraper primitivo, vi que era una mina de oro —densidad de árboles, un modelo digital de elevación, la ciudad en 3D— y lo dejé a un lado porque era mucho trabajo decodificar el sistema. En este sentido, la IA ha sido increíble. Hacerle scraping a un sistema así antes era demasiado para la mayoría de los principiantes. Cuando volví a retomarlo, simplemente le pedí a Claude que trajera cada dataset que la ciudad publica y lo procesara para mapas web —pero todavía necesitaba el modelo mental: cómo encaja todo el sistema y qué herramientas usar—.

## 11 · Los pilares de Cali

Estos son los cuatro pilares de la construcción de Cali —la respuesta a "qué herramientas usar"—. Dagster orquesta el pipeline en Python: adquirir, luego procesar. Protomaps convierte cientos de capas en un único formato de tiles moderno y eficiente. MapLibre dibuja el mapa en el navegador, con SvelteKit como un frontend liviano a su alrededor. AWS, conectado con SST, lo pone en línea.

## 12 · Paso 1 · Adquirir: el geoportal IDESC

Paso uno, adquirir. Esto es IDESC —el catálogo abierto de datos espaciales de Cali—. Todo lo que la ciudad publica vive aquí: servicios WFS y WMS, descargas, ortoimágenes, un geocodificador. Adquirir es simplemente meter esa materia prima por la puerta —bajar cada capa para que el resto del pipeline tenga sobre qué construir—.

## 13 · Paso 2 · Procesar: ¿por qué orquestar?

¿Por qué orquestar un pipeline? A esta escala —más de 350 capas, 6,6 GB de entrada— necesitas reconstruir tu resultado desde cero o parcialmente, probar su exactitud y agregar nuevas fuentes sin romper todo. Eso es lo que te da un orquestador.

## 14 · Dagster: pasar datos entre assets

Si escribes Python, Dagster es una gran opción. Es *data-first* (los datos primero): cada paso es un asset —un sustantivo, la cosa que quieres que exista—. Estos son los assets reales del pipeline del mapa de Cali, recortados. Aquí está la jugada clave: `layer_geojson` devuelve sus datos, y el siguiente asset simplemente recibe un argumento con ese mismo nombre —`def layer_pmtiles(layer_geojson)`—. Dagster conecta los dos y le entrega la salida del primer asset directamente al segundo. Los datos fluyen de un asset al siguiente; no andas haciendo malabares con archivos ni con variables globales. (Si un paso solo necesita correr *después* de otro pero no usa sus datos, escribirías `deps=[...]` en su lugar.)

Dos alternativas que vale la pena conocer: Prefect convierte Python existente en pipelines rápidamente, con menos estructura —bueno cuando tu trabajo es más verbos que sustantivos ("avísame")—. Airflow es maduro pero doloroso, sobre todo en grandes empresas y universidades.

## 15 · Digresión: data-first vs flow-first

Una pequeña digresión. "Data-first frente a flow-first" suena abstracto —esa comprensión solo llega con el tiempo—. Peter Norvig tiene un ensayo sabio, "Teach Yourself Programming in Ten Years" (Aprende a programar en diez años). Es como aprender otro idioma: en español decimos "sueño contigo", mientras que en inglés dicen "I dream *of* you" —sueño *de* ti—. Misma idea, énfasis distinto. Lo mismo pasa con estas herramientas.

## 16 · 354 capas de Cali

El resultado: 354 capas de mapa sobre Cali —árboles, ciclorrutas, zonas de inundación, tantísimo—. Parte es vieja y probablemente imprecisa, pero es increíble. Para el motor del mapa elegí Protomaps más MapLibre: casi tan potente como Mapbox, gratis y rápido en celulares económicos —algo que importa muchísimo en Colombia—. La IA escribió el código; yo elegí las herramientas. El siguiente paso es investigar y hacer llamadas para entender qué significan de verdad los datos.

Un mapa de clínicas, o de zonas con poco desarrollo, es inherentemente un mapa sobre justicia y política —lo que nos devuelve al trabajo pesado—.

## 17 · Las fosas clandestinas: 230 vs 2.000

En 2017–2018 fui parte de un equipo de periodistas mexicanos que ganó el Premio Gabo por nuestro trabajo sobre las fosas clandestinas y los desaparecidos. Construí un mapa que vieron millones de personas.

Lo que lo hizo buen periodismo de datos fue la curiosidad dirigida a la rendición de cuentas. El gobierno nacional decía que se habían encontrado unas 230 fosas. Pero las autoridades municipales y estatales también llevaban registro de fosas. Solicitamos esos registros, los sumamos —y contamos casi 2.000—. Se convirtió en un símbolo de la corrupción del gobierno.

Algo de lo que no hemos hablado todavía es que hay muchos tipos de datos: están los datos de medición, los datos de encuesta y los datos administrativos. Todos son interesantes, pero los datos administrativos suelen ser poderosos para la rendición de cuentas, porque puedes contrastar afirmaciones con el registro burocrático, o mirar lo que las instituciones poderosas _no_ registran.

## 18 · 2023: el Estado reconoce más de 5.600

Y el número nunca dejó de subir. Para 2023, el propio organismo de búsqueda del gobierno —la Comisión Nacional de Búsqueda— había reconocido más de 5.600 fosas clandestinas. La cifra por la que alguna vez nos pusieron en duda hoy queda pequeña frente al propio conteo del Estado. Esa es la recompensa de la curiosidad dirigida a la rendición de cuentas: con el tiempo, se reivindica.

## 19 · Eso lo puedo verificar

El corazón de todo esto: alguien con poder dice "la contratación de policías se está desplomando", o "la mayoría de las personas que arrestamos estaban saqueando" —y tú piensas: *eso lo puedo verificar*—. En Chicago, la policía arrestó a más personas por protestar que por saquear. A nivel nacional, los oficiales decían que renunciaban en masa; los datos laborales decían que no.

## 20 · La charla en una línea

Esa es toda la charla en una sola línea: haz la pregunta y luego ve a verificar. Gracias.

Enlaces: observablehq.com/@eads/waves-on-my-beach · data.adondevanlosdesaparecidos.org

## 21 · Actividad: Les toca

Les toca. Van a apuntar un skill de Claude hacia los datos abiertos de Colombia y a recorrer el mismo camino de toda la charla —adquirir, procesar, analizar—. Un consejo antes de empezar: trabajen en parejas. Esto funciona mejor cuando uno de ustedes va buscando cosas y dirigiendo la conversación mientras el otro explora los datos o construye —y luego se turnan—.

## 22 · Déjalo listo: instalar y clonar

Tres pasos y ya están listos para conversar. Uno — instala Claude: ya sea Claude Code (la herramienta de terminal) o Claude Desktop (la app); y ten Python 3.10+ en tu máquina —esta es una clase de Python, así que corres las cosas en tu propio computador (¿necesitas después una librería como pandas? solo pídele a Claude que la instale)—. Dos — clona el repo de la clase; el skill `colombia-open-data` viene adentro, en `.claude/skills/`, así que Claude lo encuentra automáticamente —no hay que copiar ni instalar nada—. Tres — abre la carpeta clonada en Claude: en Claude Code, corre `claude` dentro de la carpeta; en Claude Desktop, abre la carpeta y cambia a Code. De cualquier forma el skill se carga automáticamente y ya puedes preguntar —que es la siguiente diapositiva—.

## 23 · Solo pregunta, en español

No empiezas escribiendo código —simplemente preguntas, en español sencillo: "búscame el acceso a internet fijo por departamento, 2023"—. El skill hace más que traer filas: Claude encuentra el dataset correcto en datos.gov.co y **te arma un pequeño pipeline de Dagster para él —raw → clean → dashboard—, tuyo, propio**, y luego lo corre. Los números son apenas la prueba de que funcionó (Bogotá lidera con 2,25 millones). Hay dos lecciones incorporadas en ese pipeline. Primera: agrega en el servidor —`sum()` agrupado por departamento— así que trae un puñado de filas, no 2,8 millones. Segunda: fija un solo trimestre (2023-T3), porque los suscriptores son un *stock*, no un *flujo*: sumar cada trimestre contaría dos veces a las mismas personas. Te quedaste en el lenguaje de la pregunta; el skill armó la plomería —y es tuyo para conservarlo y cambiarlo—.

## 24 · Una página que puedes compartir

Después pídele a Claude que convierta esos números en algo que puedas ver y compartir: una página HTML sencilla —una gráfica de barras, una tabla, un mapita—. Sin framework, sin paso de compilación, solo un archivo que puedes abrir en el navegador o enviarle a alguien. Eso es "visualizar y publicar", a pequeña escala.

## 25 · Cosas para probar después

Hacia dónde llevarlo. Grafica o mapea algo interesante. Indaga cómo se produce un dataset —quién lo hizo, cómo, y qué falta—. Busca lugares donde los datos contradicen lo que dice la gente con poder. Cruza un dataset con otro —la legislación que ha escrito un político frente a las donaciones que ha recibido es un clásico—. Y recuerden: trabajen en parejas y túrnense.

Y vamos a cerrar la actividad todos juntos —de vuelta como un solo grupo, compartiendo lo que encontramos: qué te sorprendió, dónde te atascaste, qué quieres seguir explorando—.

# Guión fácil de leer — *¿Será que alguien está midiendo eso?*

> Versión **simplificada para leer en voz alta** (frases cortas, palabras sencillas),
> pensada para leerla del celular durante la charla. Son solo las **notas del
> presentador**, sacadas de [`slides.es.md`](slides.es.md) y reescritas más fáciles.
> El orden es el mismo que las diapositivas. Para ver estas notas al lado del deck,
> abre la presentación y presiona **S**.
>
> ¿Editaste el deck? Vuelve a generar este guión.

---

## 1 · Apertura — periodismo de datos

Soy periodista de datos. O sea: soy ingeniero, pero mi producto final son noticias e investigaciones. Hoy ustedes también lo van a ser.

Es bonito, porque usas la ciencia, la lógica y la tecnología para hacer el mundo un poco más justo y humano. Y también por pura curiosidad: para parar, mirar el mundo de otra forma y hablar con gente interesante. No me ha hecho rico, pero he conocido el mundo y he visto la historia mientras pasa.

## 2 · Temas pesados y curiosidad

Mucho de lo que hago trata de temas pesados: derechos humanos, discriminación, los desaparecidos. Este es un mapa de fosas clandestinas en México. Vamos a volver a este proyecto al final, cuando ya hayamos visto el proceso.

Pero también hago esto por gusto, por placer y por mi propia curiosidad. Vamos a empezar con ejemplos así: cosas sencillas que te harían la vida un poco mejor.

## 3 · El proceso en cinco pasos

Todo proyecto empieza con una pregunta de dos partes. La primera es algo como: ¿las multas de tránsito llevan a la gente a la quiebra? ¿Qué barrios tienen más basura?

La segunda parte es: ¿alguien midió eso?

Si la respuesta es sí, entonces: consigues los datos, los limpias, descubres qué significan, los muestras, los escribes y los publicas.

## 4 · ¿El lago está para nadar?

Empecemos con un proyecto alegre. La pregunta era: ¿hace suficiente calor para ir a nadar?

Yo vivía en Chicago, al lado de un lago enorme, casi un mar. Me encantaba salir a trotar y después tirarme al agua.

## 5 · El problema: Chicago es frío

El problema es que Chicago es frío casi todo el año. Esta foto no es mía, pero es de la misma playa, mirando hacia el otro lado, en pleno invierno. Entonces yo quería saber: ¿cuándo está el lago suficientemente tibio para mí, como para ir a nadar?

## 6 · Paso 1 · Adquirir — la API Seagull

Otra vez la pregunta: ¿será que alguien está midiendo esto? Pensé que debía haber sensores en el lago midiendo temperatura y viento. En Estados Unidos, buena parte del monitoreo ambiental es público, así que tenía una oportunidad. Y sí: con unas pocas búsquedas encontré que una universidad acababa de publicar una API con todos los sensores de los Grandes Lagos. Se llama Seagull.

Hay datos de todo tipo esperando a que alguien los use. ¿Cuántos niños se lastiman en camas elásticas? Una agencia gringa lleva esa cuenta. Y en México y Colombia hoy hay aún más datos públicos interesantes que en Estados Unidos. El problema es que están encerrados en sistemas viejos y raros.

## 7 · Paso 2 · Procesar — traer y aplanar el JSON

Procesar. Hice una consulta de los últimos días, traje el JSON y lo convertí en una sola tabla ordenada para poder analizarlo. Sin base de datos, sin archivos: lo más simple posible. (Esto empezó como un cuaderno de Observable en JavaScript; aquí es la misma idea, pero en Python.)

## 8 · Paso 3 · Analizar — la "escala sentida"

Analizar es decidir qué significan los números. Yo no tengo intuición para saber si 14 grados es muy distinto de 20, así que busqué qué consideran peligroso los científicos. Ese fue mi punto de partida. Después, cada vez que nadaba, anotaba la temperatura y cómo se sentía de verdad. Con suficientes notas, pude llevar esa experiencia de vuelta a los datos. Así armé una "escala sentida" que convierte un número en una sensación. La función `pd.cut` hace justo eso: corta la temperatura en mis bandas con nombre. 22 grados se siente perfecto después de un buen trote.

Los números son una señal. Pero es mi experiencia, junto con ellos, lo que les da sentido.

A veces el lago ya pasa de 24 grados. Se siente delicioso, pero es más alto que cualquier temperatura registrada antes. Incluso en este proyecto divertido, un pequeño recordatorio del cambio climático.

## 9 · Paso 4 · Visualizar + publicar

No puedes analizar sin visualizar. Esta gráfica y estas frases ponen mi opinión y mi experiencia del lago encima de los datos, y los muestran de una forma que se entiende mejor: la línea no solo dice la temperatura de hoy, también muestra la tendencia.

No hice mucha reportería aquí. Pero sí llamé a las personas que hacen la API, para confirmar que estaba usando bien el sistema y los números correctos. Y publiqué mi trabajo en un cuaderno público.

## 10 · De Chicago a Cali

Ahora pasamos de Chicago a Cali. Hace unos años me enamoré de alguien de aquí. Y también de la ciudad: la cultura, las montañas, el clima, la energía. Entonces, claro, quise ver qué datos podía encontrar sobre ella.

Buscando, encontré un servidor de mapas difícil de usar, pero lleno de datos increíbles. La ciudad publica muchísimo. Esto fue en 2024, antes de que la IA fuera buena con el código. Escribí un scraper básico, vi que era una mina de oro (densidad de árboles, modelo de elevación, la ciudad en 3D) y lo dejé ahí, porque entender el sistema era mucho trabajo.

Aquí la IA me cambió la vida. Antes, hacerle scraping a un sistema así era demasiado para un principiante. Cuando lo retomé, simplemente le pedí a Claude que bajara todos los datasets de la ciudad y los preparara para mapas web. Pero yo todavía necesitaba el modelo mental: cómo encaja todo el sistema y qué herramientas usar.

## 11 · Los pilares de Cali

Estos son los cuatro pilares para construir el mapa de Cali. Son la respuesta a "qué herramientas usar".

Dagster orquesta el pipeline en Python: primero adquirir, luego procesar. Protomaps convierte cientos de capas en un solo formato de tiles, moderno y eficiente. MapLibre dibuja el mapa en el navegador, y SvelteKit es un frontend liviano alrededor. AWS, con SST, lo pone en línea.

## 12 · Paso 1 · Adquirir — el geoportal IDESC

Paso uno: adquirir. Esto es IDESC, el catálogo abierto de datos espaciales de Cali. Todo lo que la ciudad publica vive aquí: servicios WFS y WMS, descargas, ortoimágenes, un geocodificador. Adquirir es simplemente meter esa materia prima por la puerta: bajar cada capa para que el resto del pipeline tenga sobre qué trabajar.

## 13 · Paso 2 · Procesar — ¿por qué orquestar?

¿Para qué orquestar un pipeline? A esta escala (más de 350 capas, 6,6 GB de entrada) necesitas poder reconstruir tu resultado, entero o por partes, comprobar que esté bien y agregar fuentes nuevas sin romper todo. Eso es lo que te da un orquestador.

## 14 · Dagster — pasar datos entre assets

Si programas en Python, Dagster es una gran opción. Es "data-first", los datos primero: cada paso es un asset. Un asset es un sustantivo, la cosa que quieres que exista. Estos son los assets reales del mapa de Cali, recortados.

La clave está aquí: `layer_geojson` devuelve sus datos, y el siguiente asset recibe un argumento con ese mismo nombre: `def layer_pmtiles(layer_geojson)`. Dagster conecta los dos y le pasa la salida del primero al segundo. Los datos fluyen de un asset al siguiente; no andas haciendo malabares con archivos ni variables globales. (Si un paso solo tiene que correr después de otro, pero no usa sus datos, usarías `deps` en su lugar.)

Dos alternativas para conocer: Prefect convierte el Python que ya tienes en pipelines, rápido y con menos estructura. Sirve cuando tu trabajo es más verbos que sustantivos ("avísame cuando..."). Airflow es maduro, pero doloroso, sobre todo en empresas y universidades grandes.

## 15 · 354 capas de Cali

El resultado: 354 capas de mapa sobre Cali. Árboles, ciclorrutas, zonas de inundación, muchísimo. Parte es vieja y seguramente imprecisa, pero es impresionante. Para el mapa elegí Protomaps con MapLibre: casi tan potente como Mapbox, gratis y rápido hasta en celulares económicos. Eso importa mucho en Colombia. La IA escribió el código; yo elegí las herramientas. El siguiente paso es investigar y llamar a la gente para entender qué significan de verdad los datos.

Un mapa de clínicas, o de zonas sin desarrollo, es también un mapa sobre justicia y política. Y eso nos devuelve al trabajo pesado.

## 16 · Las fosas: 230 vs 2.000

En 2017 y 2018 fui parte de un equipo de periodistas mexicanos. Ganamos el Premio Gabo por nuestro trabajo sobre las fosas clandestinas y los desaparecidos. Yo construí un mapa que vieron millones de personas.

Lo que lo hizo buen periodismo de datos fue la curiosidad con un objetivo: pedir cuentas. El gobierno nacional decía que se habían encontrado unas 230 fosas. Pero los municipios y los estados también llevaban su propio registro. Pedimos esos registros, los sumamos, y contamos casi 2.000. Eso se volvió un símbolo de la corrupción del gobierno.

Algo que no he dicho todavía: hay varios tipos de datos. Datos de medición, datos de encuesta y datos administrativos. Todos son interesantes, pero los administrativos suelen ser muy poderosos para pedir cuentas. Porque puedes comparar lo que dicen con el registro oficial, o mirar lo que las instituciones poderosas no registran.

## 17 · 2023: el Estado reconoce más de 5.600

Y el número nunca dejó de subir. Para 2023, el propio organismo de búsqueda del gobierno, la Comisión Nacional de Búsqueda, ya reconocía más de 5.600 fosas clandestinas. La cifra por la que alguna vez nos cuestionaron hoy se queda corta frente al conteo del mismo Estado. Esa es la recompensa de la curiosidad con un objetivo: con el tiempo, te dan la razón.

## 18 · Eso lo puedo verificar

El corazón de todo esto es simple. Alguien con poder dice "la contratación de policías se está cayendo", o "casi todos los que arrestamos estaban saqueando". Y tú piensas: eso lo puedo verificar. En Chicago, la policía arrestó a más gente por protestar que por saquear. Y a nivel nacional, los oficiales decían que renunciaban en masa; los datos de empleo decían que no.

## 19 · La charla en una línea

Esta es toda la charla en una sola frase: haz la pregunta y después ve a verificar. Gracias.

Enlaces: observablehq.com/@eads/waves-on-my-beach · data.adondevanlosdesaparecidos.org

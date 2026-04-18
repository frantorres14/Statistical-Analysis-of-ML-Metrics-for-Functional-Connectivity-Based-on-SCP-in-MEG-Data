# S1200 Human Connectome project
El conjunto de datos conocido como 1200 Subjects release (o S1200) constituye la publicación final y más completa de datos del estudio original del Human Connectome Project (HCP) del consorcio WU-Minn, enfocado en adultos jóvenes sanos. Publicado en febrero de 2017, con actualizaciones posteriores en 2018, este lanzamiento representa la culminación de la fase de recolección de datos del proyecto (2012-2015), proporcionando a la comunidad científica un recurso multimodal sin precedentes para el estudio de la conectividad cerebral y su relación con el comportamiento humano.  
El objetivo fundamental del HCP fue mapear las conexiones estructurales y funcionales del cerebro humano a una escala macroscópica. Para lograrlo, se reclutó una cohorte de 1206 adultos jóvenes sanos, con edades comprendidas entre 22 y 35 años, incluyendo una muestra enriquecida de gemelos (monocigóticos y dicigóticos) y sus hermanos no gemelos para facilitar estudios de heredabilidad.  
El protocolo de adquisición fue estandarizado rigurosamente para todos los participantes e incluyó múltiples modalidades de neuroimagen, pruebas conductuales exhaustivas y datos genéticos. Las principales modalidades de imagen fueron:  

__Resonancia Magnética (MRI) a 3 Tesla (3T):__
+ Imágenes estructurales de alta resolución (T1w, T2w)
+ Resonancia magnética funcional en estado de reposo (rfMRI)
+ Resonancia magnética funcional orientada a tareas (tfMRI)
+ Imágenes de difusión (dMRI)

__Resonancia Magnética (MRI) a 7 Tesla (7T):__
+ Resonancia magnética funcional en estado de reposo (rfMTI)
+ Resonancia magnética funcional orientado a tareas tfMRI (retinotopía y visualización de películas) 
+ Imágenes de difusión (dMRI).

__Magnetoencefalografía (MEG):__
+ Datos en estado de reposo (rMEG)
+ Datos durante la ejecución de tareas (tMEG).

El S1200 release es significativo no solo por ser grande en cuanto al número de sujetos, sino también por la profundidad y amplitud de los datos proporcionados, los cuáles Incluye:
+ 1206 sujetos con datos demográficos y conductuales.
+ Para 3T MRI incluye 1113 sujetos de los cuales 889 tienen un conjunto de datos completo en las cuatro modalidades de 3T.
+ Para 7T MRI incluye 184 sujetos de los cuales 175 tienen datos completos para todas las modalidades de 7T.
+ Para datos MEG incluye 95 sujetos de los cuales 48 sujetos tienen datos completos para todas las modalidades.
+ 46 sujetos (gemelos monocigóticos) con datos de retest, es decir, fueron escaneados y evaluados una segunda vez para estudios de fiabilidad.  

Aclarando que todos los sujetos en 7T y MEG también fueron escaneados en 3T.

## Tareas y descansos realizados por los sujetos  para cada modalidad.
La adquisición de datos de neuroimagen funcional se ha complementado con una serie de paradigmas experimentales diseñados para elucidar la actividad cerebral evocada por tareas específicas para cada modalidad (3T fMRI, 7T fMRI y MEG). A continuación, se detalla el conjunto de tareas implementadas para cada modalidad, especificando los parámetros temporales de adquisición y los períodos de descanso correspondientes.

### 1. Modalidad 3T fMRI
Para esta modalidad se diseñó una lista de siete tareas que evalúan una diversidad de sistemas neuronales, con el objetivo de identificar nodos funcionales, comparar la conectividad en reposo y en tarea, y correlacionar la actividad cerebral con diferencias individuales en el comportamiento. Los datos se adquirieron con tiempo de repetición (TR) de 720 ms, pero con duraciones de escaneo variables según la tarea. Cada tarea se realizó dos veces, alternando la dirección de codificación de fase (derecha-izquierda y izquierda-derecha) para corregir distorsiones.

La estructura de las sesiones de resonancia magnética a 3 Teslas fue estandarizada para todos los participantes y se distribuyó a lo largo de dos días. Cada día incluía una sesión de imágenes funcionales empezando con dos sesiones en estado de reposo y posteriormente se continuaba con la adquisición de los datos de las tareas evocadas, tres tareas en el primer día y cuatro tareas en el segundo día.

#### Reposo
+ Descripción de la tarea: Los participantes mantienen la vista fija en una cruz mientras permanecen en reposo.
+ Duración por corrida: 14 minutos y 33 segundos.
+ Número total de corridas: 4.
+ Número de frames (volúmenes) por corrida: 1200.
+ Períodos de descanso: No se incluyen períodos de descanso explícitos dentro de cada corrida de 15 minutos. El descanso se produce entre las diferentes corridas y sesiones de adquisición.

#### Memoria de Trabajo (Working Memory)
+ Descripción de la tarea: Esta tarea combina la evaluación de la memoria de trabajo con la identificación de representaciones específicas de categorías (rostros, lugares, herramientas y partes del cuerpo) mediante un paradigma n-back. Los sujetos realizan bloques de tareas 0-back (condición de control) y 2-back (condición de memoria de trabajo).
+ Duración por corrida: 5 minutos y 1 segundo.
+ Número de frames (volúmenes): 405.
+ Estructura: Cada corrida contiene 8 bloques de tarea de 25 segundos cada uno (10 ensayos de 2.5 segundos) y 4 bloques de fijación (descanso) de 15 segundos.

#### Juego de azar (Gambling)
+ Descripción de la tarea: Adaptada de Delgado et al. (2000), esta tarea evalúa el procesamiento de recompensa. Los participantes juegan a adivinar cartas para ganar o perder dinero.
+ Duración por corrida: 3 minutos y 12 segundos
+ Número de frames (volúmenes): 253
+ Estructura: Se presentan bloques de 8 ensayos que son predominantemente de recompensa o de pérdida. Cada corrida incluye 2 bloques de recompensa, 2 de pérdida y 4 bloques de fijación de 15 segundos.

#### Motora (Motor)
+ Descripción de la tarea: Diseñada para mapear áreas motoras, los participantes reciben indicaciones visuales para mover los dedos de la mano izquierda o derecha, los dedos del pie izquierdo o derecho, o la lengua
+ Duración por corrida: 3 minutos y 34 segundos
+ Número de frames (volúmenes): 284
+ Estructura: Cada bloque de movimiento dura 12 segundos y precedido por una señal de 3 segundos. Cada corrida contiene 13 bloques de tarea (2 de lengua, 4 de mano, 4 de pie) y 3 bloques de fijación de 15 segundos

#### Procesamiento de Lenguaje (Story-Math)
+ Descripción de la tarea: Basada en el trabajo de Binder et al. (2011), esta tarea intercala bloques en los que los sujetos escuchan breves historias y responden a una pregunta de opción múltiple, con bloques en los que resuelven problemas matemáticos presentados auditivamente.
+ Duración por corrida: 3 minutos y 57 segundos
+ Número de frames (volúmenes): 316
+ Estructura: Cada una de las dos corridas intercala 4 bloques de tarea de historia y 4 bloques de tarea de matemáticas. 

#### Cognición social (Social cognition)
+ Descripción de la tarea: Utilizando videos de formas geométricas (cuadrados, círculos, tríangulos) que interactúan de manera intencionada (mental) o se mueven al azar (random), esta tarea evalúa la Teoría de la mente. Después de cada video, los participantes juzgan si los objetos tuvieron una interacción mental, era al azar o si no estaban seguros de la interacción
+ Duración por corrida: 3 minutos y 27 segundos
+ Número de frames (volúmenes): 274
+ Estructura: Cada una de las dos corridas presenta 5 bloques de video de 20 segundos cada uno (una corrida con 2 de interacción "mental" y 3 "random", y la otra con 3 "mental" y 2 "random") y 5 bloques de fijación de 15 segundos.

#### Procesamiento Relación (Relational Processing)
+ Descripción de la tarea: Adaptada de Smith et al. (2007), esta tarea requiere que los participantes determinen si dos pares de objetos difieren en la misma dimensión (forma o textura) en la condición relacional, o si un objeto inferior coincide con alguno de los dos superiores en una dimensión específica en la condición de control
+ Duración por corrida: 2 minutos y 56 segundos
+ Número de frames (volúmenes): 232
+ Estructura: Cada corrida tiene 3 bloques de procesamiento relacional de 18 segundos (4 ensayos), 3 bloques de una condición de control de emparejamiento de 18 segundos (5 ensayos) y 3 bloques de fijación de 16 segundos

#### Procesamiento emocional (Emotion provessing)
+ Descripción de la tarea: Basada en el paradigma de Hariri et al. (2002), los sujetos deben emparejar rostros con expresiones de miedo o enojo, o emparejar formas geométricas en una condición de control
+ Duración por corrida: 2 minutos y 16 segundos
+ Número de frames (volúmenes): 176
+ Estructura: Cada corrida incluye 3 bloques de rostros y 3 bloques de formas con 8 segundos de fijación al final de cada corrida.

### 2. Modalidad 7T fMRI
En la adquisición a 7T, se implementaron paradigmas deseñados para aprovechar la mayor resolución espacial y temporal de esta modaldiad. Estos datos se adquirieron con un tiempo de repetición (TR) de 1000 ms. De manera análoga al protocolo de 3T, se adquirieron cuatro corridas de estado de reposo, cada una con una duración de aproximadamente 16 minutos. Estas corridas se distribuyeron al inicio de cada una de las cuatro sesiones de imagen a 7T. Los sujetos siguieron las mismas instrucciones: permanecer con los ojos abiertos y mantener una fijación relajada en una cruz proyectada sobre un fondo oscuro.
La estrategia de corrección de distorsiones también se adaptó, utilizando codificación de fase alternada en la dirección posterior-anterior (PA) para las corridas 1 y 3, y en la dirección anterior-posterior (AP) para las corridas 2 y 4.

#### Reposo
+ Descripción de la tarea: Los participantes mantienen la vista fija en una cruz mientras permanecen en reposo.
+ Duración por corrida: 16 minutos.
+ Número total de corridas: 4.
+ Número de frames (volúmenes) por corrida: 900.
+ Tiempo de Repetición (TR): 1000 ms.
+ Períodos de descanso: No se estructuran pausas internas durante las corridas de estado de reposo. El descanso se gestiona entre las sesiones de adquisición

#### Visualización de películas (Movie-watching)
+ Descripción de la tarea: Los sujetos visualizaron extractos de películas independientes y de Hollywood para estudiar la actividad cerebral 
+ Duración por corrida: Entre 15 minutos 1 segundo y 156 minutos 21 segundos, dependiendo del archivo de estímulo específico
+ Número de frames (volúmenes): Entre 901 y 921
+ Estructura: Los estímulos consisten en clips de video concatenados. Antes de cada clip, se presentan 20 segundos de descanso (pantalla negra con la palabra "REST"), y se incluyen otros 20 segundos de descanso al final de la película.

#### Mapeo retinotópico (retinotopy task fMRI)
+ Descripción de la tarea: Se utilizaron estímulos visuales específicos para mapear las áreas visuales de la corteza, midiendo la organización topográfica de la corteza con respecto a la ubicación del estímulo en la retina. Se aplicaron máscaras de apertura móviles sobre el patrón "mashfast" para generar el estímulo visual dinámico específico para cada una de las 6 corridas.
+ Duración por corrida: 5 minutos para cada uno de los 6 tipos de estímulos.
+ Número de frames (volúmenes) por corrida: 300
+ Estructura: 
    + RET1 (RETCCW): Barrido de cuñas giratorias de 90 grados en sentido antihorario (Counter-Clockwise). Cada ciclo de barrido duraba 32 segundos.
    + RET2 (RETCW): Mismo estímulo de cuñas, pero con rotación en sentido horario (Clockwise).
    + RET3 (RETEXP): Anillos en expansión, cuyo ancho aumentaba linealmente con la excentricidad. Cada ciclo duraba 28 segundos, seguido de 4 segundos de descanso.
    + RET4 (RETCON): Anillos en contracción, con la misma estructura temporal que los anillos en expansión.
    + RET5 (RETBAR1): Barrido de barras en múltiples direcciones (izquierda-derecha, abajo-arriba, diagonales, etc.).
    + RET6 (RETBAR2): Repetición del mismo estímulo que RETBAR1.

### 3. Modalidad MEG
Las tareas de tMEG se seleccionaron como un subconjunto de las utilizadas en 3T fMRI, con el objetivo de estudiar la dinámica temporal de la actividad neuronal con alta precisión. Se hizo un esfuerzo considerable para que las tareas fueran lo más similares posible en temporización y diseño a sus contrapartes de fMRI. El sistema de adquisición contó con 248 canales de magnetómetro y 23 canales de referencia. Los datos se registraron con una frecuencia de muestreo de 2034.5101 Hz y un ancho de banda de 400 Hz (DC-coupled).

La estructura de una sesión MEG estándar, de aproximadamente 3 horas, fue rigurosamente estandarizada para todos los sujetos. La secuencia típica de adquisición fue la siguiente:
1. Escaneo de sala vacía (Empty room scan): Una medición diaria de 5 minutos para monitorizar el ruido del sistema y del entorno.
2. Escaneo de ruido del participante (Participant noise scan): Una medición de 1 minuto para detectar artefactos magnéticos en el sujeto.
3. Digitalización de la superficie de la cabeza: Se utiliza un digitalizador Polhemus FASTRAK-III para registrar la posición de hitos anatómicos (nasión, puntos periauriculares), cinco bobinas localizadoras y la forma de la cabeza del sujeto para la posterior co-registración con la resonancia magnética estructural.
4. Tres corridas de MEG en estado de reposo (rMEG): Cada una de aproximadamente 6 minutos de duración.
5. Seis corridas de MEG de tareas (tMEG): Dos corridas para cada una de las tres tareas: Memoria de Trabajo, Procesamiento del Lenguaje (Historia-Matemáticas) y Tarea Motora.

#### Reposo
+ Descripción de la tarea: Los datos de rMEG fueron adquiridos en tres corridas consecutivas. Durante estos escaneos, los sujetos se encontraban en posición supina, con instrucciones de permanecer relajados, quietos y con los ojos abiertos, manteniendo la fijación en una cruz roja proyectada sobre un fondo oscuro en una sala oscurecida
+ Duración por corrida: 6 minmutos aproximadamente.
+ Número total de corridas: 3.


#### Memoria de trabajo (Working memory)
+ Descripción de la tarea: Los participantes realizan una tarea n-back con imágenes de rostros y herramientas, en condiciones 0 back y 2 back
+ Duración por corrida: 10 minutos
+ Estructura: Se realizan dos corridas, cada una conteniendo 16 bloques de tareas (8 de 0-Back y 8 de 2-Back; 8 de caras y 8 de herramientas). Cada bloque consiste en 10 ensayos. En cada ensayo, el estímulo se presenta por 2000 ms, seguido de un intervalo de respuesta de 500 ms. Entre los bloques de tarea se intercalan bloques de fijación de 15 segundos. Los participantes presionan un botón con el dedo índice derecho para los estímulos que coinciden ("match") y otro con el dedo medio derecho para los que no coinciden ("non-match").

#### Procesamiento del Lenguaje (Story vs. Math)
+ Descripción de la tarea: 
    + Historia (Story): Los sujetos escuchan breves historias (fábulas de Esopo) y luego responden a una pregunta de opción múltiple sobre el tema de la historia. 
    + Matemáticas (Math): Los sujetos escuchan y resuelven problemas de aritmética (sumas y restas), seguidos de una pregunta de opción forzada con dos posibles respuestas numéricas.
+ Duración por corrida: 7 minutos
+ Duración de bloques: 30 segundos aproximádamente
+ Estructura: Los participantes seleccionan la primera o la segunda opción de respuesta presionando un botón con el dedo índice o medio de la mano derecha, respectivamente.

#### Motora (Motor)
+ Descripción de la tarea: Se presentan señales visuales que instruyen al sujeto a realizar movimientos de la mano derecha, mano izquierda, pie derecho o pie izquierdo. Los movimientos específicos son golpear los dedos índice y pulgar o aprepar los dedos del pie.
+ Duración por corrida: 32 bloques de movimiento y 9 bloques de fijación. 
+ Estructura:Cada bloque de movimiento dura 12 segundos, contiene 10 movimientos indicados por una flecha que aparece en pantalla, el bloque es precedido por una señal cisual que indica el nombre y el lado a mover.


## Carpetas tmegpreproc y rmegpreproc

### Tratamiento de los Datos en la Carpeta  (Estado de Reposo)

La pipeline "rmegpreproc" se aplica exclusivamente a los datos de MEG en estado de reposo (rMEG) y tiene como objetivo producir una representación limpia de la señal a nivel de sensor, lista para análisis espectrales o de conectividad funcional.
El tratamiento de los datos sigue una secuencia metodológica precisa:
1. Segmentación de Datos: La pipeline toma los datos crudos y continuos de cada adquisición de rMEG y los segmenta en épocas o piezas de longitud fija de 2 segundos. Esta segmentación es un prerrequisito para técnicas de análisis que asumen estacionariedad en ventanas de tiempo cortas, como el cálculo del espectro de potencia.
2. Exclusión de Canales y Segmentos Defectuosos: Se utilizan los resultados de la pipeline "baddata" para identificar y remover los canales marcados como "malos" (bad channels) y los segmentos de tiempo que contienen artefactos de gran amplitud no fisiológicos (bad segments), como saltos de SQUID. Esta exclusión es crucial para asegurar la integridad de los análisis posteriores.
3. Eliminación de Artefactos mediante ICA: La pipeline utiliza la clasificación de componentes generada por la pipeline "icaclass". Los Componentes Independientes (ICs) que han sido clasificados como artefactos (p. ej., de origen cardíaco, ocular o ambiental) son proyectados fuera de los datos. Este paso de "limpieza" permite aislar la actividad neuronal de interés de las fuentes de ruido estructurado.  

El producto final de esta pipeline son archivos en formato MATLAB (.mat) que contienen una estructura de datos compatible con el software FieldTrip, con la señal rMEG limpia y segmentada. Estos archivos se encuentran en el directorio <SubjectID>/MEG/Restin/rmegpreproc/.

### Tratamiento de los Datos en la Carpeta  (Tareas)

La pipeline "tmegpreproc" es la contraparte de "rmegpreproc" para los datos de MEG de tareas (tMEG) y constituye el primer nivel de procesamiento específico para el análisis de la actividad cerebral evocada por eventos. Su tratamiento es conceptualmente similar al de rMEG, pero con una diferencia fundamental en la segmentación.
1. División en Grupos de Ensayos (Data Groups): Dado que en un mismo experimento pueden existir múltiples eventos de interés, la pipeline primero divide los datos de cada tarea en "grupos de ensayos". Cada grupo corresponde a ensayos alineados temporalmente con un evento específico. Por ejemplo, en la tarea motora, se pueden definir ensayos alineados al estímulo visual y otros alineados al inicio del movimiento (detectado por EMG).
2. Exclusión de Canales y Segmentos Defectuosos: Al igual que en rMEG, se eliminan los canales y segmentos marcados como "malos" por la pipeline "baddata". Para ensayos de longitud variable, como los bloques de la tarea de lenguaje, los segmentos defectuosos se reemplazan por valores NaN (Not a Number) en lugar de eliminarse, para así preservar la estructura temporal del ensayo.
3. Eliminación de Artefactos mediante ICA: Los componentes identificados como artefactos por la pipeline "icaclass" (p. ej., cardíacos y oculares) son proyectados fuera de la señal, depurando así los datos a nivel de canal.
4. Remuestreo de los Datos: Para reducir la carga computacional y el tamaño de los archivos, los datos limpios y segmentados son remuestreados a una cuarta parte de su frecuencia original, resultando en una nueva frecuencia de muestreo de 508.63 Hz.
5. Segmentación en Ensayos (Trials): El registro continuo se segmenta en "épocas" o "trials", donde cada trial está alineado temporalmente con el evento definitorio de su grupo de ensayo.  

El resultado son archivos .mat que contienen los datos tMEG limpios y segmentados por evento, almacenados en el directorio <SubjectID>/MEG/[TaskName]/tmegpreproc/. Estos archivos son el insumo directo para las pipelines de nivel de canal subsecuentes, como eravg (para campos relacionados con eventos) y tfavg (para representaciones tiempo-frecuencia).


Proyecto de Spark para Comparar Arquitecturas de Ejecución en Tiempo Real


	•	Motivación

En Ciencia de Datos es vital el procesamiento de información masiva en batch para entrenar modelos de machine learning. Normalmente, la arquitectura para el entrenamiento por lotes se da por sentado. Sin embargo, para el procesamiento de datos en tiempo real hay varios factores a considerar:

	•	Tipos de fuentes de datos y velocidad del flujo
	•	Ventanas de tiempo y marcas de agua
	•	Como guardar los resultados
	•	Llegada de datos (exactamente una vez, más de una vez o al menos una vez)
 
En consecuencia, es importante dominar aspectos relacionados con la arquitectura de la plataforma donde se ejecutan aplicaciones de flujos en tiempo real.

La motivación de este proyecto es desarrollar una aplicación usando Spark Structure Streaming o Kafka para capturar datos en tiempo real. Una vez con suficiente información recuperada del flujo de entrada, entrenar un modelo de clasificación o regresión lineal y probar la calidad del modelo con datos que continúan llegando en tiempo real. Es decir, se debe hacer la captura de datos en tiempo real para calcular algunos estadísticos y a continuación guardar los datos en disco para aplicar un modelo de aprendizaje automático simple. Es posible, en lugar de estadísticos, usar técnicas de aprendizaje no supervisado online como: STREAM-LOF, OLOF, DBSCAN, …

Dado que cada equipo es de dos personas, deben realizar comparaciones de la ejecución con sus computadoras personales con o sin GPUs (spark standalone), Google Colab o AWS para constatar, con la misma aplicación, el desempeño de las diferentes plataformas. Deben usar Spark UI que se puede acceder en la instalación local mediante: 

http://localhost:4040

En caso de usar AWS o Google Colab, los parámetros de ejecución de Spark UI se descargan de un servidor remoto y debe establecer un túnel para acceder a los datos de la ejecución. Deben usar al menos las seis (6) métricas indicadas para comparar el desempeño de sus arquitecturas:

	•	Tiempo de ejecución de los jobs
	•	Tiempos de los shuffle entre cada stage ya que son operaciones lentas. Por ejemplo, join y reduceByKey hacen shuffle.
	•	Cantidad de operaciones de I/O en cada stage, ya que al igual que los shuffles, son operaciones lentas.
	•	Están Scheduler Delay (Retraso esperando recursos), Executor Run Time (Tiempo real de computación) y GC Time (Tiempo de recolección de basura) que deben revisar para cada arquitectura
	•	Spill (Memoria/Disk): Si los datos exceden la memoria disponible del executor, Spark "derrama" (spills) a disco. Un alto spill es un signo de rendimiento degradado y memoria RAM insuficiente.
	•	Environment aunque no es una métrica de rendimiento directo, es fundamental para la comparación.


	•	Objetivo Específicos

	•	Desarrollar una aplicación en pySpark o scala que capture datos en tiempo real usando Spark Structure Streaming o Kafka 

	•	Probar que funcione localmente (con o sin GPUs), o en Google Colab o en AWS.

	•	Calcular indicadores estadísticos clásicos, o modelos no supervisados en tiempo real, sobre el tráfico en tiempo real.

	•	Una vez que tengan suficientes datos guardados de la captura en tiempo real, entrenar un modelo de machine learning

	•	Reactivar el flujo en tiempo real y ahora clasificar los nuevos casos que vienen en la segunda tanda de streaming. 

	•	Comparar la ejecución de la misma aplicación, con los mismos datos, en las diferentes plataformas que seleccionaron usando Spark UI. No olviden colocar capturas de pantalla que justifiquen sus argumentos.


	•	Funcionalidades

El flujo de datos constante puede provenir de una infraestructura: 

	•	IoT
	•	Casco de electroencefalogramas
	•	Sensores de robots
	•	Bolsa de valores,
	•	Tráfico sobre algún servidor de red
	•	Datos meteorológicos, etc.

Por ejemplo, los cascos de electroencefalogramas que tiene el ITAM poseen 16 sensores y cada uno lee 256 lecturas por segundo. Esto hace un total de 4096 lecturas por segundo. El flujo que seleccionen debe manejar un flujo, al menos, de esa magnitud.

Para las estadísticas básicas del streaming en tiempo real deben considerar al menos:

	•	Los valores, en caso de ser continuos, (por ejemplo, un sensor de temperatura), deben definirse por rangos y reportar las estadísticas asociadas a esos rangos. 

	•	Determinar los mínimos y máximos de los valores del flujo(s) de entrada y calcular, al menos, los promedios y varianza. La cadencia de emisión de estos reportes debe ser muy frecuente porque les servirá para construir una visualización dinámica. No olviden considerar un modelo de aprendizaje no supervisado online si les resulta útil.

	•	Para la visualización animada de los indicadores estadísticos para el flujo de entrada pueden usar PowerBI, Tableau o Qlik Sense. Además, deben mostrar los tiempos de procesamiento en las diferentes configuraciones que utilicen: (Spark Standalone con o sin GPUs), Google Colab y/o AWS.


	•	Informe

El informe debe explicar las dos arquitecturas que utilizarán, la estructura de los datos, estadísticos calculados, qué sucede ante la caída de un esclavo o desactivación de una GPU, colocar las diferencias importantes que notará durante la ejecución de la aplicación en los dos entornos de ejecución que utilicen. Deben tener unas conclusiones que interpreten los resultados. 

Como parte de la evaluación, deben mostrar la ejecución de la aplicación al profesor de la asignatura para la última semana del semestre y se les pedirá una pequeña modificación, como parte de la evaluación del examen final del curso.

Finalmente, la fecha tope para entregar su informe y código a través de Canvas, será hasta el miércoles de la 17ava semana. 

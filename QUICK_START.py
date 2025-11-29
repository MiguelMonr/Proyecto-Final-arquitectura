"""
GUÍA DE INICIO RÁPIDO - Ejemplo de Uso del Sistema Completo
"""

# ============================================================================
# PASO 1: Configurar el ambiente
# ============================================================================

"""
En terminal:

$ cd /Users/miguelmonreal/Desktop/Semestres/Otoño2025/final_proyect_arqui
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env

Editar .env si necesitas cambiar:
- OPENWEATHER_API_KEY
- DEFAULT_LAT, DEFAULT_LON
- STREAMING_UPDATE_INTERVAL
"""


# ============================================================================
# PASO 2: Usar el API Client
# ============================================================================

from src.api_client import AirPollutionClient
import json

# Crear cliente
api_key = "8b17ffa99c2f7584753e8aac2a9483df"
client = AirPollutionClient(api_key)

# Obtener datos actuales (CDMX)
lat, lon = 19.4326296, -99.3030
data = client.get_current_pollution(lat, lon)

# Inspeccionar respuesta
if data and "list" in data:
    for record in data["list"]:
        components = record.get("components", {})
        aqi = record.get("main", {}).get("aqi")
        
        print(f"AQI Level: {aqi}")
        print(f"CO: {components.get('co', 0):.2f} μg/m³")
        print(f"NO₂: {components.get('no2', 0):.2f} μg/m³")
        print(f"PM2.5: {components.get('pm2_5', 0):.2f} μg/m³")
        print(f"PM10: {components.get('pm10', 0):.2f} μg/m³")


# ============================================================================
# PASO 3: Ejecutar Dashboard
# ============================================================================

"""
En terminal:

$ cd src
$ python dashboard.py

Luego acceder a:
http://localhost:8050

Verás:
- Botones para iniciar/detener stream
- Gráfico de AQI en tiempo real
- Histograma de niveles
- Boxplot de gases
- Panel de métricas
"""


# ============================================================================
# PASO 4: Recolectar Datos (24-48 horas)
# ============================================================================

"""
El dashboard recolecta automáticamente datos en:
/data/pollution_data.json

Estructura de cada registro:
{
    "timestamp": "2025-01-15T14:30:00",
    "aqi": 3,
    "co": 234.56,
    "no": 12.34,
    "no2": 45.23,
    "o3": 67.89,
    "so2": 23.45,
    "nh3": 5.67,
    "pm25": 18.5,
    "pm10": 32.1
}

El dashboard guarda automáticamente nuevos registros cada 5 minutos.
"""


# ============================================================================
# PASO 5: Entrenar Modelo ML
# ============================================================================

from src.model_training import AQIPredictionModel

# Crear modelo
model = AQIPredictionModel(model_type="random_forest")

# Entrenar con datos acumulados
metrics = model.train("../data/pollution_data.json")

# Ver métricas
print(f"Train Accuracy: {metrics['train_accuracy']:.4f}")
print(f"Test Accuracy: {metrics['test_accuracy']:.4f}")

# Guardar modelo
model.save("../models")

# Usar modelo para predicción
test_features = {
    "co": 250.0,
    "no": 15.0,
    "no2": 50.0,
    "o3": 70.0,
    "so2": 25.0,
    "nh3": 6.0,
    "pm25": 20.0,
    "pm10": 35.0
}

prediction, confidence = model.predict_single(test_features)
print(f"Predicción: AQI Level {prediction}")
print(f"Confianza: {confidence[prediction]:.2%}")


# ============================================================================
# PASO 6: Usar Spark Streaming (Avanzado)
# ============================================================================

"""
En terminal 1 (si no ya está corriendo):
$ cd src
$ python dashboard.py

En terminal 2:
$ cd src
$ spark-submit spark_streaming.py

En terminal 3:
$ cd src
$ python api_client.py --stream --socket localhost:9999

Spark UI disponible en:
http://localhost:4040

Verás:
- Jobs tab: tiempo de ejecución
- Stages tab: shuffle time, I/O operations
- Executor tab: GC time, spill memory
- Timeline tab: scheduler delay
"""

from src.spark_streaming import AirPollutionStreaming

streaming = AirPollutionStreaming()

# Ejecutar pipeline
streaming.run_pipeline(
    data_source="socket",
    host="localhost",
    port=9999,
    output_dir="./data/streaming"
)


# ============================================================================
# PASO 7: Análisis de Datos
# ============================================================================

import pandas as pd
from src.utils import (
    classify_aqi_level,
    calculate_rolling_statistics,
    detect_outliers,
    aggregate_by_hour
)

# Cargar datos
import json
with open("../data/pollution_data.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Estadísticas móviles
stats = calculate_rolling_statistics(data, window_size=10)
print(f"AQI promedio (últimos 10): {stats['aqi']['mean']:.2f}")

# Detectar outliers
outliers = detect_outliers(data, threshold=2.0)
print(f"Outliers detectados: {len(outliers)}")

# Agregación por hora
hourly = aggregate_by_hour(data)
print(f"Datos agregados por hora: {len(hourly)}")

# Clasificar AQI
for record in data[-5:]:  # Últimos 5
    aqi_level = classify_aqi_level(record['aqi'])
    print(f"AQI {record['aqi']}: {aqi_level}")


# ============================================================================
# PASO 8: Comparar Arquitecturas
# ============================================================================

"""
Para comparar Spark Standalone vs Colab vs AWS:

1. LOCAL (Spark Standalone):
   $ spark-submit --master local[*] src/spark_streaming.py
   Captura Spark UI: http://localhost:4040/jobs

2. GOOGLE COLAB:
   !pip install pyspark
   # Instalar ngrok para Spark UI remoto
   # Ejecutar el código de Spark
   # Usar ngrok para tunnel: ngrok http 4040

3. AWS EC2:
   # Crear cluster EMR o instancia con Spark
   # Configurar security groups
   # Ejecutar: spark-submit src/spark_streaming.py
   # Tunnel: ssh -L 4040:localhost:4040 usuario@instancia

Métricas a capturar de Spark UI:
- Job Runtime (ms)
- Shuffle Time (ms)
- I/O Operations (bytes)
- Scheduler Delay (ms)
- Executor Run Time (ms)
- GC Time (ms)
- Spill Memory (MB)
- Spill Disk (MB)

Crear tabla comparativa:
Métrica          | Local  | Colab  | AWS
Job Runtime      | 150ms  | 80ms   | 120ms
Shuffle Time     | 30ms   | 15ms   | 45ms
GC Time          | 8ms    | 4ms    | 12ms
...
"""


# ============================================================================
# PASO 9: Generar Informe
# ============================================================================

"""
Informe Final debe incluir:

1. DESCRIPCIÓN DE ARQUITECTURAS
   - Configuración de cada plataforma
   - Recursos (CPU, RAM, Storage)
   - Versiones de software

2. ESTRUCTURA DE DATOS
   - Schema JSON
   - Transformaciones aplicadas

3. ESTADÍSTICOS CALCULADOS
   - Min, Max, Media, Varianza
   - Ejemplos de resultados

4. ANÁLISIS DE RENDIMIENTO
   - Gráficos de métricas
   - Screenshots de Spark UI
   - Tablas comparativas

5. CASOS DE FALLO
   - ¿Qué pasa si cae un esclavo?
   - ¿Qué pasa sin GPU?
   - Recovery y fault tolerance

6. CONCLUSIONES
   - Arquitectura más eficiente
   - Trade-offs observados
   - Recomendaciones

Archivos a entregar:
- Código fuente (GitHub)
- Informe PDF (Canvas)
- Screenshots de ejecución
- Datos de ejemplo
"""


# ============================================================================
# PASO 10: Demostración en Vivo
# ============================================================================

"""
Para demostración en la clase:

1. Preparar:
   $ python dashboard.py
   Dejar corriendo en fondo

2. Mostrar:
   - Dashboard en http://localhost:8050
   - Datos actualizándose en tiempo real
   - Spark UI en http://localhost:4040

3. Explicar:
   - Flujo de datos (API → Dashboard → Storage)
   - Estadísticos calculados
   - Modelo entrenado
   - Arquitecturas comparadas

4. Live Coding:
   - Ejecutar api_client.py
   - Hacer predicción con modelo
   - Mostrar código de Spark

5. Preguntas Comunes:
   Q: ¿Cómo manejas tolerancia a fallos?
   A: Checkpoints de Spark + JSON en disk

   Q: ¿Por qué Random Forest?
   A: Buen balance entre accuracy y velocidad

   Q: ¿Cómo escalas a más datos?
   A: Spark distribuye el procesamiento
"""


# ============================================================================
# RECURSOS ÚTILES
# ============================================================================

"""
Documentación:
- README.md - Guía completa
- PROJECT_STRUCTURE.md - Arquitectura
- IMPLEMENTATION_SUMMARY.md - Resumen

Notebooks:
- notebooks/eda.ipynb - Análisis exploratorio

APIs:
- https://openweathermap.org/api/air-pollution

Spark:
- https://spark.apache.org/docs/latest/
- http://localhost:4040 (UI local)

Dash:
- https://dash.plotly.com/

GitHub:
- Repositorio del proyecto
"""


if __name__ == "__main__":
    print(__doc__)

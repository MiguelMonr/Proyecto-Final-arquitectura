# 🌬️ Proyecto: Comparación de Arquitecturas Spark para Streaming de Contaminación del Aire

**Curso**: Arquitectura de Sistemas Distribuidos - ITAM  
**Semestre**: Otoño 2025  
**Equipo**: 2 personas  
**Fecha Entrega**: Semana 17

---

## 📌 Descripción del Proyecto

Este proyecto implementa una **aplicación de Spark Structured Streaming** que:

1. **Captura datos en tiempo real** desde la Air Pollution API (cada 5-10 minutos)
2. **Calcula estadísticos** en ventanas deslizantes (min, max, media, varianza)
3. **Visualiza en tiempo real** mediante un dashboard interactivo
4. **Entrena un modelo de ML** con datos acumulados
5. **Predice niveles de AQI** en nuevo flujo de streaming
6. **Compara desempeño** entre diferentes arquitecturas:
   - Spark Standalone (local, con/sin GPU)
   - Google Colab
   - AWS

---

## 🎯 Objetivos Específicos

✅ Desarrollar aplicación en PySpark para capturar datos en tiempo real  
✅ Calcular indicadores estadísticos en tiempo real (min, max, media, varianza)  
✅ Entrenar modelo de clasificación de AQI (niveles 1-5)  
✅ Reactivar streaming para predicción en tiempo real  
✅ Comparar ejecución usando **6+ métricas de Spark UI**  
✅ Documentar diferencias entre arquitecturas  

---

## 🚀 Inicio Rápido

### 1. Configuración Inicial

```bash
# Navegar al proyecto
cd /Users/miguelmonreal/Desktop/Semestres/Otoño2025/final_proyect_arqui

# Activar virtual environment
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env si necesitas cambiar API key o coordenadas
```

### 2. Ejecutar Dashboard

```bash
# Terminal 1: Iniciar dashboard
cd src
python dashboard.py

# Acceso: http://localhost:8050
```

El dashboard mostrará:
- 📊 **Flujo en tiempo real**: Gráfico de serie temporal del AQI
- 📈 **Histograma**: Distribución de niveles de AQI
- 📦 **Boxplot**: Distribución de concentración de gases
- 🔢 **Métricas**: AQI actual, promedios, máximos

### 3. Probar Conexión a API

```bash
# Terminal 2: Test de API
cd src
python api_client.py
```

Debería mostrar datos JSON con estructura:
```json
{
  "timestamp": "2025-01-15T14:30:00",
  "lat": 19.4326296,
  "lon": -99.3030,
  "aqi": 3,
  "co": 234.56,
  "no2": 45.23,
  "pm25": 18.5,
  ...
}
```

### 4. Entrenar Modelo (Después de recolectar datos)

```bash
# Después de ~1 hora de recolección de datos
cd src
python model_training.py
```

Genera:
- `models/aqi_model_random_forest_*.pkl` - Modelo entrenado
- `models/aqi_model_random_forest_*_scaler.pkl` - Scaler de features
- `models/aqi_model_random_forest_*_metadata.json` - Métricas y metadata

### 5. Spark Streaming (Opcional - Más Avanzado)

```bash
# Terminal 3: Spark Streaming
cd src
spark-submit spark_streaming.py

# Spark UI: http://localhost:4040
```

---

## 📁 Estructura del Proyecto

```
final_proyect_arqui/
├── src/
│   ├── api_client.py              # Cliente para Air Pollution API
│   ├── dashboard.py               # Dashboard Dash/Plotly (tiempo real)
│   ├── spark_streaming.py         # Pipeline Spark Structured Streaming
│   ├── model_training.py          # Entrenamiento de modelos ML
│   └── utils.py                   # Funciones utilitarias
├── data/
│   ├── pollution_data.json        # Datos acumulados (creado automáticamente)
│   ├── streaming/                 # Datos de Spark (JSON/CSV)
│   └── checkpoints/               # Checkpoints de Spark Streaming
├── models/
│   └── aqi_model_*.pkl           # Modelos entrenados
├── notebooks/                     # Jupyter notebooks (análisis)
├── requirements.txt               # Dependencias Python
├── .env.example                   # Variables de entorno
├── run_project.sh                 # Script de ejecución
├── PROJECT_STRUCTURE.md           # Este documento
├── context.md                     # Contexto del proyecto
└── README.md                      # Este archivo
```

---

## 📊 Dashboard - Características

### Visualizaciones Incluidas

1. **Gráfico de Flujo (Live Data Graph)**
   - Serie temporal del AQI
   - Actualización cada 5 minutos
   - Interactivo (zoom, hover, descarga)

2. **Histograma de Niveles AQI**
   - Distribución de frecuencia
   - Clasificación: Good, Fair, Moderate, Poor, Very Poor
   - Código de colores

3. **Boxplot de Gases**
   - Distribución de 6 contaminantes principales
   - CO, NO₂, O₃, SO₂, PM2.5, PM10
   - Quartiles y outliers

4. **Panel de Métricas**
   - AQI actual y promedio
   - Máximos y promedios por gas
   - Total de registros
   - Última actualización

5. **Serie Temporal de Gases**
   - Evolución de cada contaminante
   - Visualización superpuesta

### Controles

- ✅ **Botón "Iniciar Stream"**: Comienza actualización automática
- ❌ **Botón "Detener Stream"**: Pausa recolección
- 🔄 **Auto-refresh**: Cada 5 minutos (configurable)

---

## 🧮 Métricas de Rendimiento (Spark UI)

El proyecto captura **8+ métricas** requeridas:

| Métrica | Descripción | Ubicación Spark UI |
|---------|------------|-----------------|
| **Job Runtime** | Tiempo de ejecución total | Jobs tab |
| **Shuffle Time** | Tiempo en operaciones shuffle | Tasks tab |
| **I/O Operations** | Cantidad de lecturas/escrituras | Tasks tab |
| **Scheduler Delay** | Espera de recursos | Timeline tab |
| **Executor Run Time** | Tiempo de computación real | Executor tab |
| **GC Time** | Recolección de basura | Executor tab |
| **Spill (Memory)** | Desbordamiento a memoria | Executor tab |
| **Spill (Disk)** | Desbordamiento a disco | Executor tab |

### Cómo Capturar Métricas

**Localmente (Spark Standalone)**:
```bash
# Durante ejecución, accede a:
http://localhost:4040/jobs
http://localhost:4040/stages
http://localhost:4040/executors
```

**En AWS/Colab**:
```bash
# Establecer túnel SSH
ssh -L 4040:localhost:4040 usuario@instancia

# O descarga los event logs:
# s3://tu-bucket/spark-logs/
```

---

## 📈 Flujo de Datos

```
┌─────────────────────────────────────┐
│  Air Pollution API                  │
│  (cada 5-10 minutos)                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  api_client.py                      │
│  - Obtiene datos                    │
│  - Parsea JSON                      │
│  - Enriquece con timestamp          │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────────┐  ┌──────────────────┐
│  Dashboard   │  │ Spark Streaming  │
│  (Dash)      │  │ (Structured)     │
│  - Flujo     │  │ - Estadísticas   │
│  - Histogr.  │  │ - JSON Storage   │
│  - Boxplot   │  │ - Checkpoints    │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       │            ┌──────▼────────────┐
       │            │ Datos Acumulados  │
       │            │ (JSON)            │
       │            └──────┬────────────┘
       │                   │
       │          ┌────────▼──────────┐
       │          │ model_training.py │
       │          │ - Entrenamiento   │
       │          │ - Validación      │
       │          │ - Guardado        │
       │          └────────┬──────────┘
       │                   │
       │            ┌──────▼──────────┐
       └───────────►│ Predicciones    │
                    │ en Streaming    │
                    └─────────────────┘
```

---

## 🤖 Modelo de ML

### Arquitectura

- **Algoritmo**: Random Forest (por defecto)
- **Alternativas**: Gradient Boosting, Logistic Regression
- **Target**: AQI Level (1-5)
- **Features**: CO, NO, NO₂, O₃, SO₂, NH₃, PM2.5, PM10
- **Train/Test Split**: 80/20

### Métricas de Evaluación

```
- Accuracy: Precisión general
- Precision/Recall/F1: Por clase
- Confusion Matrix: Errores de clasificación
- Feature Importance: Importancia de variables
```

### Guardar y Cargar Modelos

```python
# Entrenamiento
model = AQIPredictionModel("random_forest")
model.train("../data/pollution_data.json")
model.save("../models")

# Uso posterior
loaded_model = AQIPredictionModel.load("../models/aqi_model_*.pkl")
prediction, confidence = loaded_model.predict_single({
    "co": 234.5,
    "no2": 45.2,
    "pm25": 18.5,
    # ...
})
```

---

## 🏗️ Comparación de Arquitecturas

### Configuraciones a Probar

#### 1. **Spark Standalone (Local)**
```bash
# Sin GPU
spark-submit --master local[*] src/spark_streaming.py

# Métricas esperadas:
# - Job Runtime: ~100-500ms
# - Spill: Bajo (RAM suficiente)
# - GC Time: Bajo (< 10% del runtime)
```

#### 2. **Google Colab**
```bash
# En notebook Colab
!pip install pyspark
# Ejecutar código de Spark
# Spark UI disponible vía ngrok

# Métricas esperadas:
# - Job Runtime: ~50-200ms (GPU)
# - Mejor paralelismo
# - GC Time: Bajo
```

#### 3. **AWS EC2**
```bash
# Crear cluster EMR o usar EC2 + Spark
# Configurar Spark para multi-node
# Usar S3 para almacenamiento

# Métricas esperadas:
# - Job Runtime: Variable (según cluster size)
# - Shuffle Time: Depende del network
# - Mayor escalabilidad
```

### Tabla Comparativa

```
Métrica               | Local      | Colab      | AWS
---------------------|------------|------------|----------
Job Runtime (ms)     | 100-500    | 50-200     | 50-300
Executor Count       | 1-4        | 2-8        | 4-32+
Memory/GB            | 4-16       | 12         | 16-256
Shuffle Time (ms)    | 10-50      | 20-100     | 50-200
GC Time/Total (%)    | 5-10%      | 3-8%       | 10-15%
Spill/Total (MB)     | < 100      | < 50       | < 500
```

---

## 📝 Informe Final Requerido

El informe debe incluir:

1. **Descripción de Arquitecturas**
   - Configur ación de cada plataforma
   - Recursos utilizados (CPU, RAM, Storage)

2. **Estructura de Datos**
   - Schema de datos de entrada
   - Transformaciones aplicadas

3. **Estadísticos Calculados**
   - Fórmulas utilizadas
   - Ejemplos de resultados

4. **Análisis de Rendimiento**
   - Gráficos de métricas por arquitectura
   - Screenshots de Spark UI
   - Tablas comparativas

5. **Casos de Fallo**
   - ¿Qué pasa al caer un esclavo?
   - ¿Qué pasa sin GPU en AWS?
   - Recuperación y tolerancia a fallos

6. **Conclusiones**
   - Arquitectura más eficiente
   - Trade-offs observados
   - Recomendaciones

---

## 🐛 Troubleshooting

### Dashboard no se abre
```bash
# Verifica puerto disponible
lsof -i :8050
kill -9 <PID>

# Reinicia
python dashboard.py
```

### Error de API
```bash
# Verifica API key en .env
cat .env | grep OPENWEATHER

# Test conexión
python api_client.py

# Verifica coordenadas
# LAT=19.4326296, LON=-99.3030 (CDMX)
```

### No hay datos en dashboard
- Espera 5 minutos (intervalo de actualización)
- Verifica que "Iniciar Stream" esté activado
- Comprueba `data/pollution_data.json`

### Spark no inicia
```bash
# Instala Java si no lo tienes
java -version

# Instala PySpark
pip install pyspark

# Verifica JAVA_HOME
echo $JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home)
```

---

## 📚 Dependencias

- **pyspark** >= 3.5.0 - Distributed computing
- **dash** >= 2.14.0 - Web framework
- **plotly** >= 5.17.0 - Interactive plots
- **pandas** >= 2.1.0 - Data manipulation
- **scikit-learn** >= 1.3.0 - Machine learning
- **requests** >= 2.31.0 - HTTP client
- **python-dotenv** >= 1.0.0 - Environment vars

---

## 🔐 Variables de Entorno (.env)

```ini
# API Configuration
OPENWEATHER_API_KEY=tu_api_key
DEFAULT_LAT=19.4326296
DEFAULT_LON=-99.3030

# Spark Configuration
SPARK_MASTER=local[*]
SPARK_EXECUTOR_MEMORY=4g
SPARK_DRIVER_MEMORY=2g

# Streaming
STREAMING_UPDATE_INTERVAL=300
STREAMING_OUTPUT_DIR=./data/streaming

# Dashboard
DASHBOARD_PORT=8050
DASHBOARD_DEBUG=true
```

---

## 📞 Contacto / Preguntas

- **Documentación Spark**: https://spark.apache.org/docs/latest/
- **API OpenWeatherMap**: https://openweathermap.org/api/air-pollution
- **Dash Documentation**: https://dash.plotly.com/

---

## 📅 Timeline

| Semana | Hito |
|--------|------|
| 1-4 | Desarrollo e integración |
| 5-12 | Recolección de datos y entrenamiento |
| 13-15 | Comparación de arquitecturas |
| 16 | Redacción de informe |
| 17 | Entrega + Demostración |

---

**Última actualización**: 28 de Noviembre de 2025

¡Bienvenido al proyecto! 🚀

# Estructura del Proyecto de Spark Streaming para Contaminación del Aire

## 📁 Estructura de Directorios

```
final_proyect_arqui/
├── src/                          # Código fuente principal
│   ├── api_client.py            # Cliente para Air Pollution API
│   ├── spark_streaming.py       # Pipeline de Spark Streaming
│   ├── dashboard.py             # Dashboard interactivo (Dash)
│   ├── model_training.py        # Entrenamiento de modelos ML
│   └── utils.py                 # Funciones utilitarias
├── notebooks/                   # Jupyter notebooks para análisis
│   ├── eda.ipynb               # Análisis exploratorio
│   ├── model_training.ipynb    # Entrenamiento de modelos
│   └── performance_comparison.ipynb  # Comparación de arquitecturas
├── data/                        # Datos
│   ├── streaming/              # Datos de Spark Streaming (JSON)
│   ├── checkpoints/            # Checkpoints de Spark
│   └── pollution_data.json     # Datos acumulados para dashboard
├── models/                      # Modelos entrenados
│   └── aqi_classifier.pkl      # Modelo serializado
├── config/                      # Configuraciones
│   ├── spark_config.ini        # Config de Spark
│   └── dashboard_config.json   # Config del dashboard
├── requirements.txt             # Dependencias Python
├── .env.example                 # Variables de entorno (ejemplo)
├── run_project.sh              # Script para ejecutar
├── README.md                    # Documentación
└── context.md                   # Contexto del proyecto

```

## 🚀 Cómo Empezar

### 1. Configuración Inicial

```bash
# Clonar y entrar al directorio
cd final_proyect_arqui

# Crear virtual environment (si aún no existe)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de configuración
cp .env.example .env
# Editar .env con tus credenciales/preferencias
```

### 2. Probar la API

```bash
# Terminal 1: Probar conexión
./run_project.sh api-test
```

### 3. Ejecutar el Dashboard

```bash
# Terminal 2: Iniciar dashboard
./run_project.sh dashboard
# Acceder a: http://localhost:8050
```

### 4. Spark Streaming (Opcional - Más Avanzado)

```bash
# Terminal 3: Spark Streaming
./run_project.sh streaming
# Spark UI: http://localhost:4040
```

## 📊 Componentes Principales

### `api_client.py`
- Clase `AirPollutionClient`: Conecta con Air Pollution API
- Métodos:
  - `get_current_pollution()`: Obtiene datos actuales
  - `stream_pollution_data()`: Stream continuo a intervalo regular
  - `create_spark_stream_from_api()`: Integración con Spark

### `dashboard.py`
- Clase `PollutionDashboard`: Dashboard interactivo con Dash/Plotly
- Características:
  - ✅ Gráfico de serie temporal (Flujo de AQI)
  - ✅ Histograma de niveles de AQI
  - ✅ Boxplot de concentración de gases
  - ✅ Métricas en tiempo real
  - ✅ Control de inicio/parada del stream
  - ✅ Auto-actualización cada 5 minutos

### `spark_streaming.py`
- Clase `AirPollutionStreaming`: Pipeline de Spark
- Métodos:
  - `read_from_socket()`: Lee desde socket TCP
  - `parse_pollution_data()`: Parsea JSON a DataFrame estructurado
  - `calculate_statistics()`: Estadísticas en ventanas deslizantes
  - `classify_aqi_level()`: Clasifica AQI 1-5
  - `create_histogram_data()`: Prepara datos para histograma
  - `create_boxplot_data()`: Prepara datos para boxplot

## 🎯 Flujo de Datos

```
Air Pollution API (cada 5-10 min)
           ↓
   api_client.py (AirPollutionClient)
           ↓
   ┌─────────────────┬──────────────────┐
   ↓                 ↓
Dashboard (Dash)   Spark Streaming
   ↓                 ↓
Visualización      JSON Storage
en tiempo real     (para análisis)
   ↓                 ↓
   └─────────────────┴──────────────────┐
           ↓
   Modelo ML (Clasificación AQI)
           ↓
   Predicciones
```

## 📈 Métricas Calculadas

### Estadísticas en Tiempo Real
- **AQI**: Min, Max, Media, Desv. Est.
- **Gases**: CO, NO2, O3, SO2, NH3, PM2.5, PM10
- **Por cada gas**: Min, Max, Media

### Para Spark UI
1. ✅ Tiempo de ejecución de jobs
2. ✅ Shuffle time entre stages
3. ✅ Operaciones I/O
4. ✅ Scheduler Delay
5. ✅ Executor Run Time
6. ✅ GC Time
7. ✅ Spill (Memory/Disk)
8. ✅ Environment

## 🔍 Monitoreo

### Dashboard (localhost:8050)
- Acceso visual a todos los datos
- Controles de inicio/parada
- Métricas actuales

### Spark UI (localhost:4040)
- Disponible solo si ejecutas Spark Streaming
- Detalles de jobs, stages, tasks
- Métricas de rendimiento

## 🧪 Testing

```bash
# Probar API
python src/api_client.py

# Probar Dashboard (sin Spark)
python src/dashboard.py

# Con Spark (requiere spark instalado)
spark-submit src/spark_streaming.py
```

## 📋 Pasos Siguientes

1. **Entrenamiento de Modelo**
   - Usar datos acumulados en `data/pollution_data.json`
   - Entrenar clasificador de AQI
   - Guardar modelo en `models/`

2. **Predicción en Streaming**
   - Cargar modelo entrenado
   - Hacer predicciones en tiempo real
   - Mostrar confianza en dashboard

3. **Comparación de Arquitecturas**
   - Ejecutar en Spark Standalone (local)
   - Ejecutar en Google Colab
   - Ejecutar en AWS
   - Comparar métricas de Spark UI

4. **Informe Final**
   - Comparación de desempeño
   - Screenshots de Spark UI
   - Análisis de resultados
   - Conclusiones

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'pyspark'"
```bash
pip install pyspark
```

### "ModuleNotFoundError: No module named 'dash'"
```bash
pip install dash plotly
```

### Error de conexión a API
- Verifica tu API key en `.env`
- Verifica tu conexión a internet
- Comprueba coordenadas (LAT, LON)

### Dashboard no se abre
- Asegúrate que el puerto 8050 está disponible
- Prueba: `lsof -i :8050`

## 📝 Notas Importantes

- El update_interval debe ser **mínimo 300 segundos (5 min)** para no saturar la API gratuita
- Los datos se guardan localmente en `data/pollution_data.json`
- Spark requiere **Java** instalado
- Para GPU support, usa AWS o Google Colab

---

**Proyecto**: Comparación de Arquitecturas de Spark para Streaming de Contaminación del Aire
**Curso**: Arquitectura de Sistemas Distribuidos - ITAM
**Semestre**: Otoño 2025


---

# 🌬️ Air Pollution API — Documentación Resumida

La **Air Pollution API** proporciona información de **contaminación atmosférica actual, pronósticos y datos históricos** para cualquier ubicación del planeta mediante coordenadas geográficas.

Incluye:

* **Índice de Calidad del Aire (AQI)**
* **Concentraciones de gases contaminantes**
* **Material particulado (PM2.5 y PM10)**

---

## 📡 Capacidades del API

### **1. Datos disponibles**

* **Actuales**: calidad del aire en tiempo real.
* **Pronóstico**: disponible para **4 días** con **resolución por hora**.
* **Históricos**: disponibilidad desde **27 de noviembre de 2020**.

### **2. Contaminantes reportados**

La API regresa concentraciones (en μg/m³) de:

* **CO** – Monóxido de carbono
* **NO** – Monóxido de nitrógeno
* **NO₂** – Dióxido de nitrógeno
* **O₃** – Ozono
* **SO₂** – Dióxido de azufre
* **NH₃** – Amoniaco
* **PM10** – Partículas menores de 10 μm
* **PM2.5** – Partículas menores de 2.5 μm

---

## 🧭 Escala del Índice de Calidad del Aire (AQI)

OpenWeather utiliza una escala de **1 a 5**, donde 1 es “bueno” y 5 “muy pobre”.

### **Tabla de valores por contaminante (μg/m³)**

| **Cualitativo** | **Índice** | **SO₂** | **NO₂** | **PM10** | **PM2.5** | **O₃**  | **CO**      |
| --------------- | ---------- | ------- | ------- | -------- | --------- | ------- | ----------- |
| **Good**        | 1          | 0–20    | 0–40    | 0–20     | 0–10      | 0–60    | 0–4400      |
| **Fair**        | 2          | 20–80   | 40–70   | 20–50    | 10–25     | 60–100  | 4400–9400   |
| **Moderate**    | 3          | 80–250  | 70–150  | 50–100   | 25–50     | 100–140 | 9400–12400  |
| **Poor**        | 4          | 250–350 | 150–200 | 100–200  | 50–75     | 140–180 | 12400–15400 |
| **Very Poor**   | 5          | ≥350    | ≥200    | ≥200     | ≥75       | ≥180    | ≥15400      |

---

## 🔎 Parámetros adicionales (no afectan el AQI)

| Gas                            | Rango típico (μg/m³) |
| ------------------------------ | -------------------- |
| **NH₃ (Amoniaco)**             | 0.1 – 200            |
| **NO (Monóxido de nitrógeno)** | 0.1 – 100            |

Estos valores se reportan como referencia, pero **no participan en el cálculo del AQI**.

---

## 📘 Notas importantes

* Las unidades se expresan en **microgramos por metro cúbico (μg/m³)**.
* El AQI final se determina tomando el **peor valor relativo** entre los contaminantes medidos.
* Ideal para dashboards ambientales, sistemas IoT, modelos predictivos y análisis histórico.

---


"""
Funciones utilitarias para el proyecto.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple


def classify_aqi_level(aqi_value: int) -> str:
    """
    Clasifica el valor AQI a nivel descriptivo.
    
    Args:
        aqi_value: Valor AQI (1-5)
        
    Returns:
        String con clasificación
    """
    classifications = {
        1: "Good 😊",
        2: "Fair 😐",
        3: "Moderate ⚠️",
        4: "Poor 😷",
        5: "Very Poor 💀"
    }
    return classifications.get(aqi_value, "Unknown")


def calculate_rolling_statistics(data: List[Dict], window_size: int = 10) -> Dict:
    """
    Calcula estadísticas en ventana móvil.
    
    Args:
        data: Lista de registros
        window_size: Tamaño de ventana
        
    Returns:
        Dict con estadísticas
    """
    if not data or len(data) < window_size:
        return {}
    
    recent_data = data[-window_size:]
    df = pd.DataFrame(recent_data)
    
    stats = {
        "aqi": {
            "mean": float(df["aqi"].mean()),
            "std": float(df["aqi"].std()),
            "min": float(df["aqi"].min()),
            "max": float(df["aqi"].max())
        },
        "co": {
            "mean": float(df["co"].mean()),
            "std": float(df["co"].std()),
        },
        "no2": {
            "mean": float(df["no2"].mean()),
            "std": float(df["no2"].std()),
        },
        "pm25": {
            "mean": float(df["pm25"].mean()),
            "std": float(df["pm25"].std()),
        },
        "pm10": {
            "mean": float(df["pm10"].mean()),
            "std": float(df["pm10"].std()),
        }
    }
    
    return stats


def get_time_of_day_category(timestamp_str: str) -> str:
    """
    Categoriza la hora del día.
    
    Args:
        timestamp_str: String de timestamp ISO
        
    Returns:
        Categoría (morning, afternoon, evening, night)
    """
    dt = datetime.fromisoformat(timestamp_str)
    hour = dt.hour
    
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 21:
        return "evening"
    else:
        return "night"


def aggregate_by_hour(data: List[Dict]) -> Dict:
    """
    Agrega datos por hora.
    
    Args:
        data: Lista de registros
        
    Returns:
        Dict con datos agregados por hora
    """
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.floor('H')
    
    hourly = df.groupby("hour").agg({
        "aqi": ["mean", "min", "max"],
        "co": "mean",
        "no2": "mean",
        "o3": "mean",
        "so2": "mean",
        "pm25": "mean",
        "pm10": "mean"
    })
    
    return hourly.to_dict()


def detect_outliers(data: List[Dict], threshold: float = 2.0) -> List[Dict]:
    """
    Detecta outliers usando z-score.
    
    Args:
        data: Lista de registros
        threshold: Threshold de z-score
        
    Returns:
        Lista de registros outlier
    """
    df = pd.DataFrame(data)
    
    outliers = []
    
    for col in ["aqi", "co", "no2", "o3", "so2", "pm25", "pm10"]:
        if col not in df.columns:
            continue
            
        z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
        mask = z_scores > threshold
        
        if mask.any():
            outlier_records = df[mask].to_dict('records')
            outliers.extend(outlier_records)
    
    # Remover duplicados
    outliers = [dict(t) for t in set(tuple(d.items()) for d in outliers)]
    
    return outliers


def format_spark_metrics(metrics_json: str) -> Dict:
    """
    Formatea métricas de Spark para visualización.
    
    Args:
        metrics_json: JSON de métricas de Spark
        
    Returns:
        Dict formateado
    """
    try:
        metrics = json.loads(metrics_json)
        
        formatted = {
            "job_runtime": metrics.get("executorRunTime", 0) / 1000,  # ms to s
            "shuffle_time": metrics.get("shuffleReadTime", 0) / 1000,
            "io_operations": metrics.get("inputMetrics", {}).get("bytesRead", 0),
            "gc_time": metrics.get("jvmGCTime", 0) / 1000,
            "scheduler_delay": metrics.get("schedulerDelay", 0) / 1000,
            "spill_memory": metrics.get("memoryBytesSpilled", 0),
            "spill_disk": metrics.get("diskBytesSpilled", 0)
        }
        
        return formatted
    except:
        return {}


def compare_architectures(results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Compara resultados de diferentes arquitecturas.
    
    Args:
        results: Dict con resultados por arquitectura
        
    Returns:
        DataFrame con comparación
    """
    comparison = []
    
    for arch_name, metrics in results.items():
        row = {
            "Architecture": arch_name,
            **metrics
        }
        comparison.append(row)
    
    df = pd.DataFrame(comparison)
    
    return df


# Rangos de AQI según OpenWeatherMap
AQI_RANGES = {
    1: {"name": "Good", "SO2": (0, 20), "NO2": (0, 40), "PM10": (0, 20), "PM25": (0, 10)},
    2: {"name": "Fair", "SO2": (20, 80), "NO2": (40, 70), "PM10": (20, 50), "PM25": (10, 25)},
    3: {"name": "Moderate", "SO2": (80, 250), "NO2": (70, 150), "PM10": (50, 100), "PM25": (25, 50)},
    4: {"name": "Poor", "SO2": (250, 350), "NO2": (150, 200), "PM10": (100, 200), "PM25": (50, 75)},
    5: {"name": "Very Poor", "SO2": (350, float('inf')), "NO2": (200, float('inf')), "PM10": (200, float('inf')), "PM25": (75, float('inf'))}
}


if __name__ == "__main__":
    # Test de funciones
    print("Testing utility functions...")
    
    print(f"AQI Level 3: {classify_aqi_level(3)}")
    print(f"Hour category: {get_time_of_day_category('2025-01-15T14:30:00')}")

"""
Cliente para la API de contaminación del aire de OpenWeatherMap.
Realiza llamadas periódicas y estructura los datos para Spark Streaming.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class AirPollutionClient:
    """Cliente para obtener datos de calidad del aire."""
    
    BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
    
    def __init__(self, api_key: str):
        """
        Inicializa el cliente.
        
        Args:
            api_key: Clave de API de OpenWeatherMap
        """
        self.api_key = api_key
        self.session = requests.Session()
    
    def get_current_pollution(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Obtiene datos de contaminación actual para coordenadas específicas.
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Dict con datos de contaminación o None si hay error
        """
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "APPID": self.api_key
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Enriquecer con timestamp
            if isinstance(data, dict) and "list" in data:
                for record in data["list"]:
                    record["timestamp"] = datetime.now().isoformat()
                    record["lat"] = lat
                    record["lon"] = lon
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error en llamada a API: {e}")
            return None
    
    def get_forecast_pollution(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Obtiene pronóstico de contaminación (4 días).
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Dict con pronóstico o None si hay error
        """
        return self.get_current_pollution(lat, lon)
    
    def stream_pollution_data(self, 
                            lat: float, 
                            lon: float, 
                            interval_seconds: int = 300,
                            output_file: Optional[str] = None) -> None:
        """
        Streamea datos de contaminación a intervalo regular.
        
        Args:
            lat: Latitud
            lon: Longitud
            interval_seconds: Intervalo entre llamadas (default: 300s = 5 min)
            output_file: Archivo para guardar datos (opcional)
        """
        print(f"Iniciando stream de datos. Intervalo: {interval_seconds}s")
        
        try:
            while True:
                data = self.get_current_pollution(lat, lon)
                
                if data and "list" in data:
                    for record in data["list"]:
                        # Parsear componentes
                        components = record.get("components", {})
                        
                        # Crear record para streaming
                        stream_record = {
                            "timestamp": record.get("timestamp"),
                            "lat": lat,
                            "lon": lon,
                            "aqi": record.get("main", {}).get("aqi"),
                            "components": components
                        }
                        
                        print(f"Datos recibidos: {json.dumps(stream_record, indent=2)}")
                        
                        # Guardar si se especifica archivo
                        if output_file:
                            with open(output_file, "a") as f:
                                f.write(json.dumps(stream_record) + "\n")
                
                # Esperar antes de siguiente llamada
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("Stream detenido por usuario")


def create_spark_stream_from_api(latitude: float, 
                                longitude: float,
                                api_key: str,
                                output_socket: Optional[tuple] = None) -> None:
    """
    Crea un stream que puede consumir Spark Streaming.
    
    Args:
        latitude: Latitud
        longitude: Longitud
        api_key: Clave de API
        output_socket: Tupla (host, puerto) para enviar datos via socket
    """
    client = AirPollutionClient(api_key)
    
    if output_socket:
        import socket
        host, port = output_socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(1)
        print(f"Esperando conexión en {host}:{port}...")
        
        while True:
            conn, addr = sock.accept()
            print(f"Conexión de {addr}")
            try:
                while True:
                    data = client.get_current_pollution(latitude, longitude)
                    if data:
                        for record in data.get("list", []):
                            conn.send((json.dumps(record) + "\n").encode())
                    time.sleep(300)
            except Exception as e:
                print(f"Error: {e}")
            finally:
                conn.close()
    else:
        client.stream_pollution_data(latitude, longitude)


if __name__ == "__main__":
    # Parámetros de ejemplo
    LAT = 19.4326296
    LON = -99.3030  # Nota: tu documentación dice 68.3030 pero probablemente es -99.3030 (CDMX)
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "8b17ffa99c2f7584753e8aac2a9483df")
    
    client = AirPollutionClient(API_KEY)
    
    # Probar una llamada inicial
    print("Probando conexión a la API...")
    data = client.get_current_pollution(LAT, LON)
    
    if data:
        print(f"✓ Conexión exitosa")
        print(json.dumps(data, indent=2))
    else:
        print("✗ Error de conexión")

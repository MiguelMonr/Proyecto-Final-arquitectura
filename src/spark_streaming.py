"""
Aplicación Spark Structured Streaming para procesar datos de contaminación del aire.
Calcula estadísticos en tiempo real y alimenta un dashboard.
"""

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, LongType, MapType
import json
from datetime import datetime, timedelta
import sys
import os

# Importar cliente de API
from api_client import AirPollutionClient


class AirPollutionStreaming:
    """Procesa stream de datos de contaminación del aire."""
    
    def __init__(self, app_name: str = "AirPollutionStreaming"):
        """
        Inicializa sesión Spark.
        
        Args:
            app_name: Nombre de la aplicación Spark
        """
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .getOrCreate()
        
        # Configurar para Spark UI (localhost:4040)
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Schema para los datos de contaminación
        self.schema = StructType([
            StructField("timestamp", StringType(), True),
            StructField("lat", DoubleType(), True),
            StructField("lon", DoubleType(), True),
            StructField("aqi", LongType(), True),
            StructField("co", DoubleType(), True),
            StructField("no", DoubleType(), True),
            StructField("no2", DoubleType(), True),
            StructField("o3", DoubleType(), True),
            StructField("so2", DoubleType(), True),
            StructField("nh3", DoubleType(), True),
            StructField("pm25", DoubleType(), True),
            StructField("pm10", DoubleType(), True),
        ])
    
    def read_from_socket(self, host: str = "localhost", port: int = 9999):
        """
        Lee datos de un socket (para testing).
        
        Args:
            host: Host del socket
            port: Puerto del socket
            
        Returns:
            DataFrame streaming
        """
        df = self.spark.readStream \
            .format("socket") \
            .option("host", host) \
            .option("port", port) \
            .load()
        
        return df
    
    def parse_pollution_data(self, df):
        """
        Parsea datos JSON de contaminación.
        
        Args:
            df: DataFrame streaming con datos JSON
            
        Returns:
            DataFrame con esquema estructurado
        """
        # Parsear JSON
        parsed = df.select(
            F.col("value").cast(StringType()).alias("json_str")
        ).select(
            F.from_json(F.col("json_str"), 
                       "STRUCT<timestamp:STRING, lat:DOUBLE, lon:DOUBLE, aqi:LONG, "
                       "co:DOUBLE, no:DOUBLE, no2:DOUBLE, o3:DOUBLE, so2:DOUBLE, "
                       "nh3:DOUBLE, pm25:DOUBLE, pm10:DOUBLE>")
            .alias("data")
        ).select("data.*")
        
        # Convertir timestamp
        parsed = parsed.withColumn(
            "timestamp",
            F.to_timestamp(F.col("timestamp"))
        ).withColumn(
            "date",
            F.to_date(F.col("timestamp"))
        )
        
        return parsed
    
    def calculate_statistics(self, df, window_seconds: int = 300):
        """
        Calcula estadísticas en ventanas deslizantes.
        
        Args:
            df: DataFrame streaming con datos parseados
            window_seconds: Tamaño de ventana en segundos
            
        Returns:
            DataFrame con estadísticas
        """
        stats = df.withWatermark("timestamp", "10 minutes") \
            .groupBy(
                F.window(F.col("timestamp"), f"{window_seconds} seconds")
            ).agg(
                # AQI
                F.min("aqi").alias("aqi_min"),
                F.max("aqi").alias("aqi_max"),
                F.mean("aqi").alias("aqi_mean"),
                F.stddev("aqi").alias("aqi_stddev"),
                
                # CO
                F.min("co").alias("co_min"),
                F.max("co").alias("co_max"),
                F.mean("co").alias("co_mean"),
                
                # NO2
                F.min("no2").alias("no2_min"),
                F.max("no2").alias("no2_max"),
                F.mean("no2").alias("no2_mean"),
                
                # PM2.5
                F.min("pm25").alias("pm25_min"),
                F.max("pm25").alias("pm25_max"),
                F.mean("pm25").alias("pm25_mean"),
                
                # PM10
                F.min("pm10").alias("pm10_min"),
                F.max("pm10").alias("pm10_max"),
                F.mean("pm10").alias("pm10_mean"),
                
                # Conteo
                F.count("*").alias("count")
            ).orderBy(F.desc("window"))
        
        return stats
    
    def classify_aqi_level(self, df):
        """
        Clasifica el nivel de AQI (1-5).
        
        Args:
            df: DataFrame con datos
            
        Returns:
            DataFrame con columna 'aqi_level'
        """
        return df.withColumn(
            "aqi_level",
            F.when(F.col("aqi") == 1, "Good")
             .when(F.col("aqi") == 2, "Fair")
             .when(F.col("aqi") == 3, "Moderate")
             .when(F.col("aqi") == 4, "Poor")
             .when(F.col("aqi") == 5, "Very Poor")
             .otherwise("Unknown")
        )
    
    def create_histogram_data(self, df):
        """
        Prepara datos para histograma de niveles AQI.
        
        Args:
            df: DataFrame con datos
            
        Returns:
            DataFrame para histograma
        """
        histogram = df.groupBy("aqi_level").agg(
            F.count("*").alias("count")
        ).orderBy("aqi_level")
        
        return histogram
    
    def create_boxplot_data(self, df):
        """
        Prepara datos para boxplot de gases.
        
        Args:
            df: DataFrame con datos
            
        Returns:
            DataFrame para boxplot
        """
        # Seleccionar solo columnas de gases
        gases = ["co", "no2", "o3", "so2", "pm25", "pm10"]
        
        # Restructurar para boxplot
        boxplot_data = df.select(
            F.col("timestamp"),
            *[F.col(gas) for gas in gases]
        ).withWatermark("timestamp", "10 minutes") \
         .groupBy(
             F.window(F.col("timestamp"), "5 minutes")
         ).agg(
            *[F.percentile_approx(gas, F.array(F.lit(0.25), F.lit(0.5), F.lit(0.75)))
              .alias(f"{gas}_quartiles") for gas in gases]
         )
        
        return boxplot_data
    
    def write_to_csv(self, df, path: str, mode: str = "append"):
        """
        Escribe datos a CSV para alimentar dashboard.
        
        Args:
            df: DataFrame streaming
            path: Ruta de salida
            mode: Modo de escritura (append, overwrite, ignore, error)
        """
        query = df.writeStream \
            .format("csv") \
            .option("path", path) \
            .option("checkpointLocation", f"{path}/_checkpoint") \
            .option("header", "true") \
            .mode(mode) \
            .start()
        
        return query
    
    def write_to_json(self, df, path: str, mode: str = "append"):
        """
        Escribe datos a JSON.
        
        Args:
            df: DataFrame streaming
            path: Ruta de salida
            mode: Modo de escritura
        """
        query = df.writeStream \
            .format("json") \
            .option("path", path) \
            .option("checkpointLocation", f"{path}/_checkpoint") \
            .mode(mode) \
            .start()
        
        return query
    
    def write_to_console(self, df, name: str = "data"):
        """
        Escribe datos a consola para debugging.
        
        Args:
            df: DataFrame streaming
            name: Nombre para identificar el stream
        """
        query = df.writeStream \
            .format("console") \
            .option("numRows", 20) \
            .option("truncate", False) \
            .start()
        
        return query
    
    def run_pipeline(self, 
                    data_source: str = "socket",
                    host: str = "localhost",
                    port: int = 9999,
                    output_dir: str = "../data/streaming"):
        """
        Ejecuta el pipeline completo.
        
        Args:
            data_source: Fuente de datos ("socket", "file", etc)
            host: Host del socket
            port: Puerto del socket
            output_dir: Directorio de salida
        """
        
        print("Iniciando pipeline de Spark Streaming...")
        
        # Leer datos
        if data_source == "socket":
            raw_df = self.read_from_socket(host, port)
        else:
            raise ValueError(f"Data source no soportada: {data_source}")
        
        # Parsear datos
        parsed_df = self.parse_pollution_data(raw_df)
        
        # Clasificar AQI
        classified_df = self.classify_aqi_level(parsed_df)
        
        # Calcular estadísticas
        stats_df = self.calculate_statistics(parsed_df)
        
        # Preparar datos para visualizaciones
        histogram_df = self.create_histogram_data(classified_df)
        
        # Escribir datos a almacenamiento
        os.makedirs(output_dir, exist_ok=True)
        
        query1 = self.write_to_json(parsed_df, f"{output_dir}/raw_data")
        query2 = self.write_to_json(stats_df, f"{output_dir}/statistics")
        query3 = self.write_to_json(histogram_df, f"{output_dir}/histogram")
        
        # Mostrar en consola
        query4 = self.write_to_console(parsed_df, "Raw Data")
        query5 = self.write_to_console(stats_df, "Statistics")
        
        print("Queries iniciadas. Spark UI: http://localhost:4040")
        print("Presiona Ctrl+C para detener")
        
        # Esperar a que terminen
        self.spark.streams.awaitAnyTermination()


def main():
    """Función principal."""
    streaming = AirPollutionStreaming()
    
    # Ejecutar pipeline
    streaming.run_pipeline(
        data_source="socket",
        host="localhost",
        port=9999,
        output_dir="./data/streaming"
    )


if __name__ == "__main__":
    main()

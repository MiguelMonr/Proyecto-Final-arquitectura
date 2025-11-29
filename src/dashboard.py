"""
Dashboard interactivo en tiempo real usando Dash y Plotly.
Visualiza el flujo de datos, histogramas y boxplots de contaminación del aire.
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

# Importar cliente de API
from api_client import AirPollutionClient


class PollutionDashboard:
    """Dashboard para visualizar datos de contaminación del aire."""
    
    def __init__(self, api_key: str, lat: float, lon: float, update_interval: int = 300):
        """
        Inicializa el dashboard.
        
        Args:
            api_key: Clave de API de OpenWeatherMap
            lat: Latitud
            lon: Longitud
            update_interval: Intervalo de actualización en segundos
        """
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.update_interval = update_interval
        self.client = AirPollutionClient(api_key)
        self.data_file = "../data/pollution_data.json"
        
        # Crear archivo de datos si no existe
        Path(self.data_file).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f:
                json.dump([], f)
        
        # Inicializar app de Dash
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
        
        # Thread para actualizar datos
        self.update_thread = None
        self.running = False
    
    def load_data(self) -> list:
        """Carga datos del archivo."""
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except:
            return []
    
    def save_data(self, data: list):
        """Guarda datos al archivo."""
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def update_data_from_api(self):
        """Actualiza datos desde la API."""
        data = self.load_data()
        
        # Obtener datos nuevos
        response = self.client.get_current_pollution(self.lat, self.lon)
        
        if response and "list" in response:
            for record in response["list"]:
                components = record.get("components", {})
                aqi_value = record.get("main", {}).get("aqi", 0)
                
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "aqi": aqi_value,
                    "co": components.get("co", 0),
                    "no": components.get("no", 0),
                    "no2": components.get("no2", 0),
                    "o3": components.get("o3", 0),
                    "so2": components.get("so2", 0),
                    "nh3": components.get("nh3", 0),
                    "pm25": components.get("pm2_5", 0),
                    "pm10": components.get("pm10", 0),
                }
                
                data.append(entry)
        
        # Mantener solo últimos 1000 registros
        data = data[-1000:]
        self.save_data(data)
    
    def background_update_worker(self):
        """Worker para actualizar datos en background."""
        while self.running:
            try:
                self.update_data_from_api()
                print(f"[{datetime.now()}] Datos actualizados")
            except Exception as e:
                print(f"Error actualizando datos: {e}")
            
            time.sleep(self.update_interval)
    
    def setup_layout(self):
        """Configura el layout del dashboard."""
        
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("🌬️ Monitor de Contaminación del Aire"),
                html.P(f"Ubicación: {self.lat}°, {self.lon}°"),
                html.P(f"Actualización: cada {self.update_interval} segundos")
            ], style={
                "backgroundColor": "#1f77b4",
                "color": "white",
                "padding": "20px",
                "marginBottom": "20px",
                "borderRadius": "5px",
                "textAlign": "center"
            }),
            
            # Controles
            html.Div([
                html.Button(
                    "Iniciar Stream",
                    id="start-btn",
                    n_clicks=0,
                    style={
                        "padding": "10px 20px",
                        "marginRight": "10px",
                        "backgroundColor": "#2ca02c",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer"
                    }
                ),
                html.Button(
                    "Detener Stream",
                    id="stop-btn",
                    n_clicks=0,
                    style={
                        "padding": "10px 20px",
                        "backgroundColor": "#d62728",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer"
                    }
                ),
                html.Span(
                    "Estado: Detenido",
                    id="status",
                    style={"marginLeft": "20px", "fontSize": "16px"}
                )
            ], style={
                "marginBottom": "20px",
                "padding": "10px",
                "backgroundColor": "#f0f0f0",
                "borderRadius": "5px"
            }),
            
            # Interval para actualizar
            dcc.Interval(
                id="update-interval",
                interval=self.update_interval * 1000,  # Convertir a ms
                n_intervals=0
            ),
            
            # Fila 1: Flujo de datos y métricas
            html.Div([
                html.Div([
                    dcc.Graph(id="live-data-graph")
                ], style={"width": "70%", "display": "inline-block", "marginRight": "2%"}),
                
                html.Div([
                    html.Div(id="metrics-panel")
                ], style={"width": "28%", "display": "inline-block", "verticalAlign": "top"})
            ], style={"marginBottom": "20px"}),
            
            # Fila 2: Histograma y Boxplot
            html.Div([
                html.Div([
                    dcc.Graph(id="aqi-histogram")
                ], style={"width": "48%", "display": "inline-block", "marginRight": "2%"}),
                
                html.Div([
                    dcc.Graph(id="gases-boxplot")
                ], style={"width": "48%", "display": "inline-block"})
            ], style={"marginBottom": "20px"}),
            
            # Fila 3: Detalles técnicos
            html.Div([
                dcc.Graph(id="gases-timeseries")
            ]),
            
            # Hidden div para almacenar datos
            html.Div(id="data-store", style={"display": "none"})
            
        ], style={
            "fontFamily": "Arial, sans-serif",
            "padding": "20px",
            "backgroundColor": "#f9f9f9",
            "margin": "0"
        })
    
    def setup_callbacks(self):
        """Configura callbacks de actualización."""
        
        @self.app.callback(
            [Output("status", "children"),
             Output("data-store", "children")],
            [Input("start-btn", "n_clicks"),
             Input("stop-btn", "n_clicks"),
             Input("update-interval", "n_intervals")]
        )
        def handle_controls(start_clicks, stop_clicks, n_intervals):
            if start_clicks > 0 and not self.running:
                self.running = True
                self.update_thread = threading.Thread(target=self.background_update_worker)
                self.update_thread.daemon = True
                self.update_thread.start()
                status = "✓ Estado: En ejecución"
            elif stop_clicks > 0 and self.running:
                self.running = False
                status = "✗ Estado: Detenido"
            else:
                status = "✓ Estado: En ejecución" if self.running else "✗ Estado: Detenido"
            
            # Actualizar datos
            self.update_data_from_api()
            data = self.load_data()
            
            return status, json.dumps(data)
        
        @self.app.callback(
            Output("live-data-graph", "figure"),
            [Input("update-interval", "n_intervals")]
        )
        def update_live_graph(n_intervals):
            data = self.load_data()
            if not data:
                return go.Figure().add_annotation(text="Sin datos")
            
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df["aqi"],
                mode="lines+markers",
                name="AQI",
                line=dict(color="#1f77b4", width=2),
                hovertemplate="<b>Tiempo:</b> %{x}<br><b>AQI:</b> %{y}<extra></extra>"
            ))
            
            fig.update_layout(
                title="Flujo de datos en tiempo real - Índice de Calidad del Aire",
                xaxis_title="Tiempo",
                yaxis_title="AQI Level (1-5)",
                hovermode="x unified",
                template="plotly_white",
                height=400
            )
            
            return fig
        
        @self.app.callback(
            Output("aqi-histogram", "figure"),
            [Input("update-interval", "n_intervals")]
        )
        def update_histogram(n_intervals):
            data = self.load_data()
            if not data:
                return go.Figure().add_annotation(text="Sin datos")
            
            df = pd.DataFrame(data)
            
            # Clasificar AQI
            aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            df["aqi_label"] = df["aqi"].map(aqi_labels)
            
            counts = df["aqi_label"].value_counts().sort_index()
            
            fig = go.Figure(data=[
                go.Bar(
                    x=counts.index,
                    y=counts.values,
                    marker_color=["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728", "#9467bd"],
                    text=counts.values,
                    textposition="auto"
                )
            ])
            
            fig.update_layout(
                title="Histograma de Niveles de AQI",
                xaxis_title="Nivel de Calidad del Aire",
                yaxis_title="Frecuencia",
                template="plotly_white",
                height=400
            )
            
            return fig
        
        @self.app.callback(
            Output("gases-boxplot", "figure"),
            [Input("update-interval", "n_intervals")]
        )
        def update_boxplot(n_intervals):
            data = self.load_data()
            if not data:
                return go.Figure().add_annotation(text="Sin datos")
            
            df = pd.DataFrame(data)
            
            # Seleccionar gases principales
            gases = ["co", "no2", "o3", "so2", "pm25", "pm10"]
            
            fig = go.Figure()
            
            for gas in gases:
                if gas in df.columns:
                    fig.add_trace(go.Box(
                        y=df[gas],
                        name=gas.upper(),
                        boxmean="sd"
                    ))
            
            fig.update_layout(
                title="Boxplot de Concentración de Gases (μg/m³)",
                yaxis_title="Concentración",
                template="plotly_white",
                height=400,
                showlegend=True
            )
            
            return fig
        
        @self.app.callback(
            Output("gases-timeseries", "figure"),
            [Input("update-interval", "n_intervals")]
        )
        def update_timeseries(n_intervals):
            data = self.load_data()
            if not data:
                return go.Figure().add_annotation(text="Sin datos")
            
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            gases = ["co", "no2", "o3", "so2", "pm25", "pm10"]
            
            fig = go.Figure()
            
            for gas in gases:
                if gas in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df["timestamp"],
                        y=df[gas],
                        mode="lines",
                        name=gas.upper()
                    ))
            
            fig.update_layout(
                title="Serie Temporal de Concentraciones de Gases",
                xaxis_title="Tiempo",
                yaxis_title="Concentración (μg/m³)",
                template="plotly_white",
                height=400,
                hovermode="x unified"
            )
            
            return fig
        
        @self.app.callback(
            Output("metrics-panel", "children"),
            [Input("update-interval", "n_intervals")]
        )
        def update_metrics(n_intervals):
            data = self.load_data()
            if not data:
                return html.Div("Sin datos")
            
            df = pd.DataFrame(data)
            
            # Última medición
            last = df.iloc[-1]
            
            # Estadísticas
            aqi_mean = df["aqi"].mean()
            co_max = df["co"].max()
            pm25_mean = df["pm25"].mean()
            
            metrics = html.Div([
                html.H3("📊 Métricas Actuales"),
                html.Hr(),
                
                html.P([
                    html.Strong("AQI Actual: "),
                    html.Span(f"{last['aqi']}", style={"fontSize": "24px", "color": "#1f77b4"})
                ]),
                
                html.P([
                    html.Strong("AQI Promedio: "),
                    f"{aqi_mean:.2f}"
                ]),
                
                html.P([
                    html.Strong("CO Máximo: "),
                    f"{co_max:.2f} μg/m³"
                ]),
                
                html.P([
                    html.Strong("PM2.5 Promedio: "),
                    f"{pm25_mean:.2f} μg/m³"
                ]),
                
                html.P([
                    html.Strong("Total Registros: "),
                    f"{len(df)}"
                ]),
                
                html.Hr(),
                html.P(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
            ], style={
                "padding": "15px",
                "backgroundColor": "white",
                "borderRadius": "5px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
            })
            
            return metrics
    
    def run(self, debug: bool = True, port: int = 8050):
        """
        Ejecuta el dashboard.
        
        Args:
            debug: Modo debug
            port: Puerto de ejecución
        """
        print(f"🚀 Dashboard disponible en http://localhost:{port}")
        self.app.run_server(debug=debug, port=port)


def main():
    """Función principal."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Parámetros
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "8b17ffa99c2f7584753e8aac2a9483df")
    LAT = 19.4326296
    LON = -99.3030  # CDMX
    
    # Crear y ejecutar dashboard
    dashboard = PollutionDashboard(
        api_key=API_KEY,
        lat=LAT,
        lon=LON,
        update_interval=300  # 5 minutos
    )
    
    dashboard.run(debug=True, port=8050)


if __name__ == "__main__":
    main()

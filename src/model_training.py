"""
Entrenamiento de modelos de ML para predicción de AQI.
Usa datos acumulados del stream para entrenar clasificadores.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_recall_fscore_support
)
import joblib
import json
import os
from pathlib import Path
from datetime import datetime


class AQIPredictionModel:
    """Modelo para predicción del índice de calidad del aire."""
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Inicializa el modelo.
        
        Args:
            model_type: Tipo de modelo ('random_forest', 'gradient_boosting', 'logistic_regression')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.classes = None
        self.metrics = {}
        
        # Crear modelo base
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        elif model_type == "logistic_regression":
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Tipo de modelo no soportado: {model_type}")
    
    def load_training_data(self, data_file: str) -> pd.DataFrame:
        """
        Carga datos de entrenamiento desde JSON.
        
        Args:
            data_file: Ruta del archivo de datos
            
        Returns:
            DataFrame con datos
        """
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # Eliminar filas con valores faltantes
        df = df.dropna()
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """
        Prepara features para el modelo.
        
        Args:
            df: DataFrame con datos
            
        Returns:
            Tupla (X, y) con features y target
        """
        # Features: gases + AQI histórico
        feature_cols = ['co', 'no', 'no2', 'o3', 'so2', 'nh3', 'pm25', 'pm10']
        
        # Target: AQI
        target_col = 'aqi'
        
        # Verificar que todas las columnas existen
        available_features = [col for col in feature_cols if col in df.columns]
        
        X = df[available_features].values
        y = df[target_col].values
        
        self.feature_names = available_features
        
        return X, y
    
    def train(self, 
             data_file: str,
             test_size: float = 0.2,
             validation_size: float = 0.1) -> dict:
        """
        Entrena el modelo.
        
        Args:
            data_file: Ruta del archivo de datos
            test_size: Proporción de datos de test
            validation_size: Proporción de datos de validación
            
        Returns:
            Dict con métricas de entrenamiento
        """
        print(f"Cargando datos desde {data_file}...")
        df = self.load_training_data(data_file)
        
        print(f"Dataset size: {len(df)}")
        
        # Preparar features
        X, y = self.prepare_features(df)
        
        self.classes = np.unique(y)
        print(f"Clases: {self.classes}")
        print(f"Distribución: {np.bincount(y)}")
        
        # Split en train y test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Escalado de features
        print("Escalando features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenamiento
        print(f"Entrenando modelo {self.model_type}...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluación
        print("Evaluando modelo...")
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        train_accuracy = accuracy_score(y_train, train_pred)
        test_accuracy = accuracy_score(y_test, test_pred)
        
        print(f"Train Accuracy: {train_accuracy:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        
        # Reportes detallados
        print("\nClassification Report (Test Set):")
        print(classification_report(y_test, test_pred))
        
        print("\nConfusion Matrix (Test Set):")
        print(confusion_matrix(y_test, test_pred))
        
        # Guardar métricas
        self.metrics = {
            "model_type": self.model_type,
            "timestamp": datetime.now().isoformat(),
            "train_accuracy": float(train_accuracy),
            "test_accuracy": float(test_accuracy),
            "train_size": len(X_train),
            "test_size": len(X_test),
            "features": self.feature_names,
            "classes": list(self.classes),
            "precision_recall_fscore": classification_report(
                y_test, test_pred, output_dict=True
            )
        }
        
        return self.metrics
    
    def predict(self, X: np.ndarray) -> tuple:
        """
        Hace predicciones.
        
        Args:
            X: Features para predicción
            
        Returns:
            Tupla (predicciones, probabilidades)
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Usa train() primero.")
        
        # Escalar features
        X_scaled = self.scaler.transform(X)
        
        # Predicciones
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return predictions, probabilities
    
    def predict_single(self, features: dict) -> tuple:
        """
        Predice para un único registro.
        
        Args:
            features: Dict con valores de features
            
        Returns:
            Tupla (predicción, confianza)
        """
        # Crear array en orden de features
        X = np.array([[features.get(feat, 0) for feat in self.feature_names]])
        
        pred, probs = self.predict(X)
        
        return pred[0], probs[0]
    
    def save(self, output_dir: str = "../models") -> str:
        """
        Guarda el modelo.
        
        Args:
            output_dir: Directorio de salida
            
        Returns:
            Ruta del modelo guardado
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Nombre del archivo
        filename = f"aqi_model_{self.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        filepath = os.path.join(output_dir, filename)
        
        # Guardar modelo y scaler
        joblib.dump(self.model, filepath)
        
        scaler_filepath = filepath.replace(".pkl", "_scaler.pkl")
        joblib.dump(self.scaler, scaler_filepath)
        
        # Guardar metadata
        metadata_filepath = filepath.replace(".pkl", "_metadata.json")
        with open(metadata_filepath, 'w') as f:
            json.dump({
                "model_file": filename,
                "feature_names": self.feature_names,
                "classes": list(self.classes),
                "metrics": self.metrics
            }, f, indent=2)
        
        print(f"✓ Modelo guardado en {filepath}")
        print(f"✓ Scaler guardado en {scaler_filepath}")
        print(f"✓ Metadata guardado en {metadata_filepath}")
        
        return filepath
    
    @staticmethod
    def load(model_path: str) -> 'AQIPredictionModel':
        """
        Carga un modelo guardado.
        
        Args:
            model_path: Ruta del modelo
            
        Returns:
            Instancia de AQIPredictionModel
        """
        # Cargar metadata
        metadata_path = model_path.replace(".pkl", "_metadata.json")
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Crear instancia
        model = AQIPredictionModel(metadata["model_file"].split("_")[2])
        
        # Cargar modelo y scaler
        model.model = joblib.load(model_path)
        scaler_path = model_path.replace(".pkl", "_scaler.pkl")
        model.scaler = joblib.load(scaler_path)
        
        model.feature_names = metadata["feature_names"]
        model.classes = np.array(metadata["classes"])
        
        print(f"✓ Modelo cargado desde {model_path}")
        
        return model


def main():
    """Función principal para entrenamiento."""
    
    # Ruta de datos
    data_file = "../data/pollution_data.json"
    
    if not os.path.exists(data_file):
        print(f"Error: {data_file} no encontrado")
        print("Primero debes recolectar datos ejecutando el dashboard")
        return
    
    # Crear y entrenar modelo
    print("="*50)
    print("ENTRENAMIENTO DE MODELO AQI")
    print("="*50)
    
    model = AQIPredictionModel(model_type="random_forest")
    
    metrics = model.train(data_file)
    
    # Guardar modelo
    model.save()
    
    print("\n" + "="*50)
    print("ENTRENAMIENTO COMPLETADO")
    print("="*50)


if __name__ == "__main__":
    main()

# /scripts/api.py
import pandas as pd
from fastapi import FastAPI, Query
from datetime import date
import os

app = FastAPI()

# Cargar los datos una sola vez al iniciar la API
RUTA_PROCESADA = os.path.join(os.path.dirname(__file__), "..", "data", "processed_catalogo.csv")

try:
    df_sismos = pd.read_csv(RUTA_PROCESADA)
    df_sismos['time_value'] = pd.to_datetime(df_sismos['time_value'])
except FileNotFoundError:
    print(f"Error: No se encontró el archivo procesado en {RUTA_PROCESADA}. Asegúrate de ejecutar main.py primero.")
    df_sismos = pd.DataFrame() # Crear un DF vacío para evitar errores de inicio

@app.get("/sismos/query")
def query_sismos(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    min_magnitude: float = Query(3.5, description="Magnitud mínima")
):
    """
    Filtra los sismos por rango de fechas y magnitud mínima.
    """
    if df_sismos.empty:
        return {"error": "Datos no cargados. Verifique el log de la API."}

    # 1. Filtrar por fechas
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    filtro_fecha = (df_sismos['time_value'] >= start_dt) & \
                   (df_sismos['time_value'] <= end_dt)
    
    # 2. Filtrar por magnitud
    filtro_magnitud = df_sismos['magnitude_value_P'] >= min_magnitude
    
    # Aplicar todos los filtros
    df_filtrado = df_sismos[filtro_fecha & filtro_magnitud]

    # Devolver los resultados en formato JSON
    return df_filtrado.to_dict(orient='records')
# app_streamlit_sismos.py
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Monitoreo Sísmico Ecuador", layout="wide")
st.title("🌋 Monitoreo de la Actividad Sísmica en Ecuador")

DATA_DIR = Path("data")
RAW_TXT = DATA_DIR / "cat_origen_2012-jul2025.txt"  # ajusta el nombre si cambia
CLEAN_CSV = DATA_DIR / "sismos_clean.csv"

# ---------- Helpers ----------
def categorize_magnitude(m):
    try:
        m = float(m)
    except:
        return "Desconocido"
    if m < 3.5:            return "Menor <3.5"
    if 3.5 <= m <= 4.9:    return "Ligero 3.5-4.9"
    if 5.0 <= m <= 5.9:    return "Moderado 5.0-5.9"
    if 6.0 <= m <= 6.9:    return "Fuerte 6.0-6.9"
    if 7.0 <= m <= 7.9:    return "Mayor 7.0-7.9"
    return "Gran >8"

def categorize_depth(d):
    try:
        d = float(d)
    except:
        return "Desconocido"
    if d < 70:             return "Superficial"
    if 70 <= d <= 300:     return "Intermedio"
    return "Profundo"

@st.cache_data
def load_or_build():
    # Si ya existe limpio, cargar
    if CLEAN_CSV.exists():
        df = pd.read_csv(CLEAN_CSV, parse_dates=['time_utc','time_ec'])
        return df

    if not RAW_TXT.exists():
        st.error(f"No se encontró {RAW_TXT}. Colócalo en /data.")
        st.stop()

    # Leer archivo IG-EPN (CSV con comas, líneas de comentario '#', espacios tras comas)
    raw = pd.read_csv(
        RAW_TXT,
        sep=",",
        comment="#",
        skipinitialspace=True
    )

    # Renombrar a corto (ajusta si tus columnas difieren)
    # Columnas típicas presentes: time_value, time_value_ms, latitude_value, longitude_value, depth_value,
    # magnitude_value_P, magnitude_type_P, magnitude_value_M, etc.
    col_map = {
        "time_value": "time_utc",
        "latitude_value": "lat",
        "longitude_value": "lon",
        "depth_value": "depth_km",
        "magnitude_value_P": "mag",
        "magnitude_type_P": "mag_type",
    }
    # Mantener solo las claves que existan
    mapped = {k: v for k, v in col_map.items() if k in raw.columns}
    df = raw.rename(columns=mapped)

    # Validar columnas mínimas
    needed = ["time_utc","lat","lon","depth_km","mag"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        st.error(f"Faltan columnas en el archivo para el dashboard: {missing}")
        st.stop()

    # Convertir tipos
    df["time_utc"] = pd.to_datetime(df["time_utc"], errors="coerce")
    for c in ["lat","lon","depth_km","mag"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Limpiar nulos críticos
    df = df.dropna(subset=["time_utc","lat","lon","depth_km","mag"]).copy()

    # Hora local Ecuador (UTC-5)
    df["time_ec"] = df["time_utc"] - pd.Timedelta(hours=5)

    # Enriquecer
    dt = df["time_ec"]  # usamos hora local para agrupar/mostrar
    df["year"]  = dt.dt.year
    df["month"] = dt.dt.month
    df["day"]   = dt.dt.day
    df["mag_category"]   = df["mag"].apply(categorize_magnitude)
    df["depth_category"] = df["depth_km"].apply(categorize_depth)

    # Guardar limpio para próximas ejecuciones
    df.to_csv(CLEAN_CSV, index=False)
    return df

df = load_or_build()

# ---------- Sidebar filtros ----------
with st.sidebar:
    st.header("Filtros")
    # Rango de fecha local
    min_date = df["time_ec"].min().date()
    max_date = df["time_ec"].max().date()
    date_range = st.date_input("Rango de fechas (hora local)", (min_date, max_date),
                               min_value=min_date, max_value=max_date)
    # Magnitud mínima
    min_mag = float(np.floor(df["mag"].min()*10)/10) if not df.empty else 0.0
    max_mag = float(np.ceil(df["mag"].max()*10)/10) if not df.empty else 10.0
    mag_min_sel = st.slider("Magnitud mínima", min_value=min_mag, max_value=max_mag,
                            value=min(4.0, max_mag), step=0.1)
    # Categorías
    mag_cat = st.multiselect("Categoría de magnitud", sorted(df["mag_category"].unique().tolist()))
    depth_cat = st.multiselect("Categoría de profundidad", sorted(df["depth_category"].unique().tolist()))
    # Selector de tipo de tiempo para gráficos agregados
    agg = st.radio("Agrupar series por", ["Año","Mes"], index=0, horizontal=True)

# ---------- Aplicar filtros ----------
dff = df.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    dff = dff[(dff["time_ec"] >= pd.to_datetime(date_range[0])) &
              (dff["time_ec"] <= pd.to_datetime(date_range[1]))]

dff = dff[dff["mag"] >= mag_min_sel]
if mag_cat:
    dff = dff[dff["mag_category"].isin(mag_cat)]
if depth_cat:
    dff = dff[dff["depth_category"].isin(depth_cat)]

# ---------- KPIs ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Sismos (filtro)", f"{len(dff):,}")
k2.metric("Magnitud media", f"{dff['mag'].mean():.2f}" if len(dff) else "—")
k3.metric("Profundidad media (km)", f"{dff['depth_km'].mean():.1f}" if len(dff) else "—")
k4.metric("Ventana total", f"{df['time_ec'].min().date()} → {df['time_ec'].max().date()}")

# ---------- MAPA ----------
st.subheader("🗺️ Mapa interactivo de sismos (hora local)")
if dff.empty:
    st.info("No hay registros con los filtros seleccionados.")
else:
    center = [float(dff['lat'].mean()), float(dff['lon'].mean())] if len(dff) else [-1.5, -78.5]
    m = folium.Map(location=center, zoom_start=6)
    for _, r in dff.iterrows():
        color = 'red' if r['mag'] >= 5 else ('orange' if r['mag'] >= 3.5 else 'blue')
        folium.CircleMarker(
            location=[r['lat'], r['lon']],
            radius=max(2, r['mag']*1.5),
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=f"Mag {r['mag']:.1f} | Prof {r['depth_km']:.0f} km<br>{r['time_ec']}"
        ).add_to(m)
    st_folium(m, width=950, height=540)

# ---------- HISTOGRAMA DE MAGNITUD ----------
st.subheader("📊 Distribución de magnitudes")
if len(dff):
    fig_hist = px.histogram(dff, x="mag", nbins=40, title="Histograma de magnitudes")
    fig_hist.update_layout(xaxis_title="Magnitud (mag)", yaxis_title="Conteo")
    st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.info("Ajusta los filtros para ver el histograma.")

# ---------- SERIES: Sismos por año/mes ----------
st.subheader("📈 Sismos por período")
if len(dff):
    if agg == "Año":
        ser = dff.groupby(dff["time_ec"].dt.year).size().reset_index(name="count").rename(columns={"time_ec":"year"})
        ser = ser.rename(columns={"time_ec":"year"})
        xcol = "time_ec"
        ser.columns = ["time_ec","count"]
        ser["time_ec"] = ser["time_ec"].astype(int)
        fig_bar = px.bar(ser, x="time_ec", y="count", title="Número de sismos por año",
                         labels={"time_ec":"Año","count":"Sismos"})
    else:
        # Por mes (Año-Mes)
        dm = dff.set_index("time_ec").resample("M").size().reset_index(name="count")
        fig_bar = px.bar(dm, x="time_ec", y="count", title="Número de sismos por mes",
                         labels={"time_ec":"Fecha (Y-M)","count":"Sismos"})
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Ajusta los filtros para ver la serie por período.")

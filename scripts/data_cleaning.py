import pandas as pd


def limpiar_datos(catalogo):
    catalogo.columns = catalogo.columns.str.strip()
    # Convertir la columna de tiempo al formato datetime
    catalogo['time_value'] = pd.to_datetime(catalogo['time_value'], errors='coerce')

    # Convertir columnas numéricas
    catalogo['latitude_value'] = pd.to_numeric(catalogo['latitude_value'], errors='coerce')
    catalogo['longitude_value'] = pd.to_numeric(catalogo['longitude_value'], errors='coerce')
    catalogo['depth_value'] = pd.to_numeric(catalogo['depth_value'], errors='coerce')
    catalogo['magnitude_value_P'] = pd.to_numeric(catalogo['magnitude_value_P'], errors='coerce')

    # Eliminar filas vacías importantes
    catalogo = catalogo.dropna(subset=['time_value', 'latitude_value', 'longitude_value', 'magnitude_value_P'])

    # Crear categorías de magnitud
    def clasificar_magnitud(m):
        if m < 3.5:
            return 'Menor'
        elif m < 5.0:
            return 'Ligero'
        elif m < 6.0:
            return 'Moderado'
        elif m < 7.0:
            return 'Fuerte'
        else:
            return 'Mayor'
    catalogo['categoria_magnitud'] = catalogo['magnitude_value_P'].apply(clasificar_magnitud)

    # Categorías por profundidad
    def clasificar_profundidad(d):
        if d < 70:
            return 'Superficial'
        elif d < 300:
            return 'Intermedio'
        else:
            return 'Profundo'
    catalogo['categoria_profundidad'] = catalogo['depth_value'].apply(clasificar_profundidad)

    return catalogo

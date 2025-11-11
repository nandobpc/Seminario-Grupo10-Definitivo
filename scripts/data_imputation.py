import pandas as pd

def imputar_datos(catalogo):
    # Quitar espacios de nombres de columnas por si acaso
    catalogo.columns = catalogo.columns.str.strip()

    # Imputar valores faltantes en columnas numéricas principales
    for col in ['latitude_value', 'longitude_value', 'depth_value', 'magnitude_value_P']:
        if col in catalogo.columns:
            catalogo[col] = catalogo[col].fillna(catalogo[col].mean())
        else:
            print(f" Columna {col} no encontrada, se omite imputación.")

    # Imputar texto faltante en 'Fuente' y 'methodID'
    for col in ['Fuente', 'methodID']:
        if col in catalogo.columns:
            catalogo[col] = catalogo[col].fillna('Desconocido')

    print(" Imputación completada. Sin valores nulos críticos.")
    return catalogo

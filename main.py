import os
from scripts.data_loader import cargar_catalogo_sismico
from scripts.data_cleaning import limpiar_datos
from scripts.data_imputation import imputar_datos
from scripts.data_visualizacion import graficar_datos

# Ruta del archivo
ruta_datos = os.path.join("data", "cat_origen_2012-jul2025.txt")

# Cargar datos
catalogo = cargar_catalogo_sismico(ruta_datos)
print("Datos cargados:", catalogo.shape)

# Ver nombres de columnas para identificar la columna de fecha
print("Columnas disponibles:", catalogo.columns)

# Limpiar datos
catalogo = limpiar_datos(catalogo)
print("Datos limpiados:", catalogo.shape)

# Imputar datos
catalogo = imputar_datos(catalogo)
print("Datos imputados:", catalogo.shape)

# Mostrar muestra
print(catalogo.head())

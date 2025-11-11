import pandas as pd
import os

# CONFIGURACIÓN DE RUTAS

# ruta absoluta del script actual
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ruta del archivo de datos
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "cat_origen_2012-jul2025.txt")


# FUNCIÓN PARA CARGAR DATOS

def cargar_catalogo_sismico(path):
    print(f"\nCargando catálogo sísmico desde:\n{path}\n")
    try:
        # leer el archivo .txt separado por comas
        df = pd.read_csv(path, sep=",", comment="#")
        print(" Datos cargados correctamente.")
        print(f"Filas cargadas: {len(df)}\n")
        return df

    except FileNotFoundError:
        print(f" Error: no se encontró el archivo en {path}")
        print("Asegúrate de que el archivo esté en la carpeta 'data'.")
        return None

    except pd.errors.ParserError as e:
        print(f" Error al leer el archivo: {e}")
        print("Verifica si el separador correcto es ',' o ';' o '\\t'.")
        return None

    except Exception as e:
        print(f" Ocurrió un error inesperado: {e}")
        return None


# BLOQUE PRINCIPAL

if __name__ == "__main__":
    print(f"Ejecutando script desde: {os.path.abspath(__file__)}")

    # cargar el catálogo sísmico
    catalogo = cargar_catalogo_sismico(DATA_PATH)

    # mostrar información general
    if catalogo is not None:
        print("\n--- Primeras 5 filas del catálogo ---")
        print(catalogo.head())

        print("\n--- Información del DataFrame ---")
        catalogo.info()

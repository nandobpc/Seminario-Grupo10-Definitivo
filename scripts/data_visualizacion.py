import plotly.express as px
def graficar_datos(catalogo):
    # Quitar espacios de columnas por seguridad
    catalogo.columns = catalogo.columns.str.strip()

    # =======  1. Mapa de eventos sísmicos =======
    fig_mapa = px.scatter_geo(
        catalogo,
        lat='latitude_value',
        lon='longitude_value',
        color='magnitude_value_P',
        hover_name='Fuente',
        size='magnitude_value_P',
        color_continuous_scale='Turbo',
        title='Mapa de eventos sísmicos (Magnitud y ubicación)',
        projection='natural earth'
    )
    fig_mapa.show()

    # =======  2. Histograma de magnitudes =======
    fig_mag = px.histogram(
        catalogo,
        x='magnitude_value_P',
        nbins=40,
        title='Distribución de magnitudes',
        color_discrete_sequence=['indianred']
    )
    fig_mag.show()

    # =======  3. Dispersión Magnitud vs Profundidad =======
    fig_disp = px.scatter(
        catalogo,
        x='depth_value',
        y='magnitude_value_P',
        color='magnitude_value_P',
        color_continuous_scale='Viridis',
        title='Relación entre profundidad y magnitud'
    )
    fig_disp.show()

    print(" Visualizaciones generadas con exito.")
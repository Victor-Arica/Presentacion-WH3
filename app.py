import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from geopandas import GeoSeries
from shapely.geometry import Point, LineString
import folium as fm
from folium import Marker, GeoJson
from folium.plugins import MarkerCluster, HeatMap, StripePattern


# Cargar datos con caché para mejor performance
@st.cache_data
def load_data():
    # Cargar shapefile de distritos (ajusta la ruta según tu estructura de archivos)
    dpt_shp = gpd.read_file("shape_file/DISTRITOS.shp")

    # Cargar datos de escuelas (ajusta la ruta)
    final_df = pd.read_excel("archivo_final.xlsx", engine='openpyxl')

    # Seleccionar columnas relevantes
    columnas = [
        "Código Modular", "Nombre de SS.EE.", "Ubigeo", "Departamento",
        "Provincia", "Distrito", "Centro Poblado", "Nivel / Modalidad",
        "Gestion / Dependencia"
    ]
    final_df = final_df[columnas]

    # Preparar datos
    gdf_escuelas = final_df.copy()
    gdf_escuelas = gdf_escuelas.rename(columns={
        "Distrito": "DISTRITO",
        "Ubigeo": "IDDIST"
    })

    # Convertir a mayúsculas y tipos de datos consistentes
    gdf_escuelas["DISTRITO"] = gdf_escuelas["DISTRITO"].str.upper()
    dpt_shp["DISTRITO"] = dpt_shp["DISTRITO"].str.upper()
    gdf_escuelas['IDDIST'] = gdf_escuelas['IDDIST'].astype(int)
    dpt_shp['IDDIST'] = dpt_shp['IDDIST'].astype(int)

    # Filtrar por nivel educativo
    dt_inicial = gdf_escuelas[gdf_escuelas['Nivel / Modalidad'].str.contains(
        'Inicial', case=False)]
    dt_primaria = gdf_escuelas[gdf_escuelas['Nivel / Modalidad'].str.contains(
        'Primaria', case=False)]
    dt_secundaria = gdf_escuelas[gdf_escuelas['Nivel / Modalidad'].str.contains(
        'Secundaria', case=False)]

    # Calcular cantidad de escuelas por distrito
    cantidad_inicial = dt_inicial.groupby(
        'IDDIST').size().reset_index(name='NumEscuelas')
    cantidad_primaria = dt_primaria.groupby(
        'IDDIST').size().reset_index(name='NumEscuelas')
    cantidad_secundaria = dt_secundaria.groupby(
        'IDDIST').size().reset_index(name='NumEscuelas')

    # Merge con shapefiles
    dpt_inicial = dpt_shp.merge(
        cantidad_inicial, on='IDDIST', how='left').fillna({'NumEscuelas': 0})
    dpt_primaria = dpt_shp.merge(
        cantidad_primaria, on='IDDIST', how='left').fillna({'NumEscuelas': 0})
    dpt_secundaria = dpt_shp.merge(
        cantidad_secundaria, on='IDDIST', how='left').fillna({'NumEscuelas': 0})

    return {
        'dpt_shp': dpt_shp,
        'dpt_inicial': dpt_inicial,
        'dpt_primaria': dpt_primaria,
        'dpt_secundaria': dpt_secundaria,
        'departamentos': dpt_shp[['IDDPTO', 'DEPARTAMEN']].drop_duplicates()
    }


# Titulo
st.title("Presentación de Datos Geoespaciales de escuelas en Perú")

# Cargar los datos una vez
data = load_data()

# Crear pestañas
tabs = st.tabs(["Data Description", "Static Maps", "Dynamic Maps"])

with tabs[0]:
    st.header("Descripción de los Datos")


with tabs[1]:
    st.header("Mapas Estáticos")

    st.subheader(
        "Distribución de escuelas de Nivel Inicial por distrito a nivel país")
    img1 = Image.open(r"imagen/Inicial.png")
    st.image(img1, use_container_width=True)
    st.subheader(
        "Distribución de escuelas de Nivel Primaria por distrito a nivel país")
    img2 = Image.open(r"imagen/Primaria.png")
    st.image(img2, use_container_width=True)

    st.subheader(
        "Distribución de escuelas de Nivel Secundaria por distrito a nivel país")
    img3 = Image.open(r"imagen/Secundaria.png")
    st.image(img3, use_container_width=True)

    st.subheader("Distribución de escuelas por departamento")
    st.write(
        "Selecciona un departamento para ver su distribución de escuelas por distrito.")
    # Crear dos columnas para los selectores
    col1, col2 = st.columns(2)

    with col1:
        # Selector de nivel educativo
        nivel = st.selectbox(
            "Seleccione el nivel educativo:",
            options=['Inicial', 'Primaria', 'Secundaria'],
            index=0
        )

    with col2:
        # Selector de departamento con nombre y código
        departamentos = data['departamentos'].sort_values('DEPARTAMEN')
        depa = st.selectbox(
            "Seleccione departamento:",
            options=departamentos['IDDPTO'],
            format_func=lambda x: f"{x} - {departamentos[departamentos['IDDPTO'] == x]['DEPARTAMEN'].values[0]}"
        )

    # Obtener datos según selección
    nivel_map = {
        'Inicial': data['dpt_inicial'],
        'Primaria': data['dpt_primaria'],
        'Secundaria': data['dpt_secundaria']
    }

    try:
        # Filtrar datos
        dpt_filtrado = nivel_map[nivel][nivel_map[nivel]['IDDPTO'] == depa]
        nomdepa = dpt_filtrado['DEPARTAMEN'].unique()[0]

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 8))
        dpt_filtrado.plot(
            column='NumEscuelas',
            cmap='Reds',
            ax=ax,
            legend=True,
            edgecolor='black',
            linewidth=0.3,
            legend_kwds={'label': 'Cantidad de Escuelas',
                         'orientation': 'horizontal'}
        )

        ax.set_title(f'Escuelas de {nivel} en {nomdepa}', fontsize=14)
        ax.axis('off')

        # Mostrar el mapa
        st.pyplot(fig)

        # Mostrar datos adicionales
        with st.expander("Ver estadísticas detalladas"):
            st.write(f"Total de escuelas: {dpt_filtrado['NumEscuelas'].sum()}")
            st.write(
                f"Distritos con datos: {len(dpt_filtrado[dpt_filtrado['NumEscuelas'] > 0])}")

    except Exception as e:
        st.error(f"Error al generar el mapa: {str(e)}")
        st.write("Por favor verifique las selecciones y vuelva a intentar")


with tabs[2]:
    st.header("Mapas Dinámicos")
    st.write("Aquí puedes poner un mapa interactivo con `folium`, `pydeck`, etc.")

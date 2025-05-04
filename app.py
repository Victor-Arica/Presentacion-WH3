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
from streamlit_folium import folium_static


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


@st.cache_data
def load_data2():
    # Cargar shapefile y datos
    dpt_shp = gpd.read_file("shape_file/DISTRITOS.shp")
    final_df = pd.read_excel("archivo_final.xlsx", engine='openpyxl')

    # Crear geometría de puntos
    geometry = [Point(lon, lat) for lon, lat in zip(
        final_df['Longitud'], final_df['Latitud'])]
    dt_colegio = gpd.GeoDataFrame(final_df, geometry=geometry, crs="EPSG:4326")

    # Filtrar departamentos
    dt_cole = dt_colegio[dt_colegio['Departamento'].isin(
        ['AYACUCHO', 'HUANCAVELICA'])]

    # Separar por nivel educativo
    dt_cole_prim = dt_cole[dt_cole['Nivel / Modalidad']
                           .str.contains('Primaria', case=False)]
    dt_cole_sec = dt_cole[dt_cole['Nivel / Modalidad']
                          .str.contains('Secundaria', case=False)]

    # Reprojectar a UTM
    primarias_m = dt_cole_prim.to_crs(epsg=32718)
    secundarias_m = dt_cole_sec.to_crs(epsg=32718)

    # Crear buffers de 5km
    primarias_m['buffer5km'] = primarias_m.geometry.buffer(5000)

    # Unión espacial
    buffers = gpd.GeoDataFrame(
        geometry=primarias_m['buffer5km'], crs=primarias_m.crs)
    secundarias_en_buffers = gpd.sjoin(
        secundarias_m, buffers, predicate='within')

    # Conteo de secundarias
    conteo_secundarias = secundarias_en_buffers.groupby('index_right').size()
    primarias_m['secundcerc'] = primarias_m.index.map(
        conteo_secundarias).fillna(0)

    # Encontrar máximos y mínimos
    max_coles = primarias_m['secundcerc'].max()
    min_coles = primarias_m['secundcerc'].min()

    list_max = primarias_m[primarias_m['secundcerc']
                           == max_coles].to_crs(epsg=4326)
    list_min = primarias_m[primarias_m['secundcerc']
                           == min_coles].to_crs(epsg=4326)

    return {
        'list_max': list_max,
        'list_min': list_min,
        'dt_cole_prim': dt_cole_prim,
        'primarias_m': primarias_m
    }

# Función para crear el mapa interactivo


def create_interactive_map(data):
    # Centrar el mapa
    meanlat = data['dt_cole_prim']['geometry'].y.mean()
    meanlon = data['dt_cole_prim']['geometry'].x.mean()

    m = fm.Map(location=[meanlat, meanlon], zoom_start=8)

    # Añadir círculos para mínimos
    for _, row in data['list_min'].iterrows():
        if not row['geometry'].is_empty:
            lat = row['geometry'].y
            lon = row['geometry'].x
            popup_text = f"Nombre: {row['Nombre de SS.EE.']}<br>Secundarias cercanas: 0"
            fm.Circle(
                radius=5000,
                location=[lat, lon],
                popup=popup_text,
                color="#ff0000",
                fill=True,
                fill_color="#ff0000",
                fill_opacity=0.4
            ).add_to(m)

    # Añadir círculos para máximos
    for _, row in data['list_max'].iterrows():
        if not row['geometry'].is_empty:
            lat = row['geometry'].y
            lon = row['geometry'].x
            popup_text = f"MAX: {int(row['secundcerc'])} secundarias<br>Nombre: {row['Nombre de SS.EE.']}"
            fm.Circle(
                radius=5000,
                location=[lat, lon],
                popup=popup_text,
                color="#00ff00",
                fill=True,
                fill_color="#00ff00",
                fill_opacity=0.4
            ).add_to(m)

    # Añadir marcadores especiales
    if not data['list_max'].empty:
        max_row = data['list_max'].iloc[0]
        fm.Marker(
            location=[max_row['geometry'].y, max_row['geometry'].x],
            icon=fm.Icon(color="green", icon="info-sign"),
            popup=f"Max: {int(max_row['secundcerc'])} secundarias"
        ).add_to(m)

    if not data['list_min'].empty:
        min_row = data['list_min'].iloc[0]
        fm.Marker(
            location=[min_row['geometry'].y, min_row['geometry'].x],
            icon=fm.Icon(color="red", icon="info-sign"),
            popup="0 secundarias cercanas"
        ).add_to(m)

    return m


# Titulo
st.title("Presentación de Datos Geoespaciales de escuelas en Perú")

# Cargar los datos una vez
data = load_data()

# Crear pestañas
tabs = st.tabs(["Data Description", "Static Maps", "Dynamic Maps"])

with tabs[0]:
    st.header("Descripción de los Datos")
    st.write("Los datos utilizados en esta presentación provienen de la base de datos del Ministerio de Educación del Perú. Se han procesado y filtrado para obtener información relevante sobre la distribución de escuelas por nivel educativo y su gestión.")
    st.write("A continuación se presenta una tabla con la clasificación de los tipos de gestión de las escuelas.")
    st.markdown("### 🏫 Clasificación de Instituciones Educativas en Perú")
    st.markdown("""
| Categoría | Tipo de gestión         | Descripción                                                                 |
|-----------|-------------------------|-----------------------------------------------------------------------------|
| **Pública** | Sector Educación       | Administradas directamente por el Ministerio de Educación o las Direcciones Regionales de Educación. Son gratuitas y constituyen la forma más común de educación pública. |
|            | En convenio            | Gestionadas por entidades privadas mediante convenios con el Estado. Educación gratuita con financiamiento público. |
|            | Municipalidad          | Escuelas gestionadas por gobiernos locales. La administración depende de la municipalidad. |
|            | Otro Sector Público    | Administradas por otras entidades del Estado (Fuerzas Armadas, Policía Nacional, otros ministerios). |
| **Privada** | Particular             | Financiadas y gestionadas por entidades privadas. Financiamiento mediante pensiones. |
|            | Parroquial             | Administradas por la Iglesia Católica u otras entidades religiosas. Educación a bajo costo/gratuita en zonas vulnerables. |
|            | Instituciones Benéficas | Gestionadas por fundaciones benéficas. Educación gratuita o de bajo costo para poblaciones vulnerables. |
|            | Comunal                | Creadas y gestionadas por comunidades locales. Financiamiento y administración comunitarios. |
|            | Cooperativa            | Gestionadas por cooperativas de docentes o padres. Toma de decisiones cooperativas. |
|            | Fiscalizada            | Privadas sujetas a supervisión estatal para cumplimiento de estándares. |
""")
    st.write("La siguiente tabla describe los campos presentes en la base de datos.")
    st.markdown("""
| Campo                  | Descripción                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| Código Modular         | Código único de identificación de la institución                           |
| Anexo                  | Número de anexo si aplica                                                  |
| Nombre de SS.EE.       | Nombre oficial de la institución educativa                                 |
| Ubigeo                 | Código de ubicación geográfica estandarizado                               |
| Departamento           | Departamento donde se ubica la institución                                 |
| Provincia              | Provincia donde se ubica la institución                                    |
| Distrito               | Distrito donde se ubica la institución                                     |
| Código DRE/UGEL        | Código de la Dirección Regional/Unidad de Gestión Educativa Local          |
| DRE / UGEL             | Nombre de la Dirección Regional/UGEL                                       |
| Centro Poblado         | Nombre del centro poblado donde se ubica                                   |
| Código Centro Poblado  | Código del centro poblado                                                  |
| Dirección              | Dirección física de la institución                                         |
| Latitud                | Coordenada geográfica (latitud)                                            |
| Longitud               | Coordenada geográfica (longitud)                                           |
| Altitud                | Altitud sobre el nivel del mar                                             |
""")
    st.markdown("""
### 📌 **Contexto de los Datos**
Esta dataset integra información oficial del **Ministerio de Educación del Perú (Minedu)** y registros georreferenciados, permitiendo:
- Identificar patrones de distribución de instituciones educativas.
- Analizar la cobertura educativa por tipo de gestión y región.
- Integrar variables socioespaciales para estudios de accesibilidad.

**Fuentes clave:**
- Padrón Oficial de Instituciones Educativas (Minedu)
- Sistema de Información de Apoyo a la Gestión de la Institución Educativa (SIAGIE)
- Geoportal Nacional de Infraestructura de Datos Espaciales (IDEP)

**Impacto:** Utilizado en políticas públicas para reducir brechas educativas y optimizar la asignación de recursos (ej: programa [Escuelas Bicentenario](https://www.gob.pe/escuelasbicentenario)).
""")

with tabs[1]:
    st.header("Mapas Estáticos")

    st.subheader(
        "Distribución de escuelas de Nivel Inicial por distrito a nivel país")
    img1 = Image.open(r"imagen/inicial.png")
    st.image(img1, use_container_width=True)
    st.subheader(
        "Distribución de escuelas de Nivel Primaria por distrito a nivel país")
    img2 = Image.open(r"imagen/primaria.png")
    st.image(img2, use_container_width=True)

    st.subheader(
        "Distribución de escuelas de Nivel Secundaria por distrito a nivel país")
    img3 = Image.open(r"imagen/secundaria.png")
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
                         'orientation': 'vertical'}
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
    st.write("En este mapa interactivo, puedes ver la distribución de escuelas de nivel primaria, que cuenta con una secundaria cercana al rededor de un radio de 5km en Ayacucho y Huancavelica.")
    st.write("Los círculos verdes indican la máxima cantidad de secundarias cercanas, mientras que los círculos rojos indican la mínima cantidad (0).")
    data_analisis = load_data2()

    # Crear y mostrar mapa
    mapa_cobertura = create_interactive_map(data_analisis)
    folium_static(mapa_cobertura, width=1000, height=600)

    # Mostrar estadísticas
    with st.expander("Estadísticas detalladas"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Máximo de secundarias cercanas",
                      int(data_analisis['list_max']['secundcerc'].max()))
        with col2:
            st.metric("Escuelas sin secundarias cercanas",
                      len(data_analisis['list_min']))


st.divider()
st.caption("_Los datos no son solo números: son huellas del mundo. Como las sombras en la caverna de Platón, apuntan a realidades más profundas que solo esperan ser interpretadas._")

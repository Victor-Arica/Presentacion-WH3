#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
#from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt 
#import chardet
import folium as fm
from folium import Marker, GeoJson
from folium.plugins import MarkerCluster, HeatMap, StripePattern


import geopandas as gpd
from geopandas import GeoSeries
from shapely.geometry import Point, LineString

import os

# In[2]:


dpt_shp = gpd.read_file(r'C:\Users\HP\OneDrive - Universidad del Pacífico\textos\Escritorio\2025-1\Git\PC\PC3\shape_file\DISTRITOS.shp')

# In[13]:


final_df = pd.read_excel(r'C:\Users\HP\OneDrive - Universidad del Pacífico\textos\Escritorio\2025-1\Git\PC\PC3\archivo_final.xlsx')


# In[ ]:


# No Correr más de una vez
# Crear geometría de puntos a partir de las coordenadas de latitud y longitud
geometry = [Point(lon, lat) for lon, lat in zip(final_df['Longitud'], final_df['Latitud'])]

# Crear un GeoDataFrame de las escuelas
dt_colegio = gpd.GeoDataFrame(final_df, geometry=geometry)

# si es none usar set_crs, si quiere cambiar usar to_crs
# Cambiar el sistema de coordenadas a EPSG:4326 (WGS 84)
dt_colegio['geometry'] = dt_colegio['geometry'].set_crs(epsg=4326)
print(dt_colegio['geometry'].crs)

#Separar la data
dt_cole = dt_colegio[(dt_colegio['Departamento'] == 'AYACUCHO') | (dt_colegio['Departamento'] == 'HUANCAVELICA')]
dt_cole_prim = dt_cole[dt_cole['Nivel / Modalidad'].str.contains('Primaria', case=False)]
dt_cole_sec = dt_cole[dt_cole['Nivel / Modalidad'].str.contains('Secundaria', case=False)]

# In[ ]:


# 4. Reprojectar a un CRS en metros (UTM zona 18S para Perú)
primarias_m = dt_cole_prim.to_crs(epsg=32718)
secundarias_m = dt_cole_sec.to_crs(epsg=32718)

# 5. Crear buffers de 5 km alrededor de las primarias
primarias_m['buffer5km'] = primarias_m.geometry.buffer(5000)  # 5000 metros = 5 km

# 6. Realizar unión espacial para encontrar secundarias dentro de los buffers
buffers = gpd.GeoDataFrame(geometry=primarias_m['buffer5km'], crs=primarias_m.crs)
secundarias_en_buffers = gpd.sjoin(secundarias_m, buffers, predicate='within')

# 7. Contar cuántas secundarias caen en cada buffer
conteo_secundarias = secundarias_en_buffers.groupby('index_right').size()
primarias_m['secundcerc'] = primarias_m.index.map(conteo_secundarias).fillna(0)



# In[97]:


max_coles =  primarias_m['secundcerc'].max()
min_coles =  primarias_m['secundcerc'].min()
list_max = primarias_m[primarias_m['secundcerc']== max_coles]
list_min = primarias_m[primarias_m['secundcerc']== min_coles]
list_min = list_min.to_crs(epsg=4326)
list_max = list_max.to_crs(epsg=4326)


# In[102]:


list_max

# In[116]:


import folium as fm
meanlat = dt_cole_prim['geometry'].y.mean()
meanlon = dt_cole_prim['geometry'].x.mean()

# 1. Crear el mapa centrado en Perú (ajusta el zoom y centro si quieres)
a = fm.Map(location=[meanlat, meanlon], zoom_start=8)

# 2. Añadir los centroides como marcadores
for _, row in list_min.iterrows():
    if row['geometry'] is not None:
        lat = row['geometry'].y
        lon = row['geometry'].x
        nombre = f"Nombre: {row['Nombre de SS.EE.']} y tiene 0 secundarias"
        
       
        fm.Circle(
              radius = 5000,
              fill=True,
              color="#db213a",
              fill_color="#db213a",
              location=[lat, lon],
              popup=nombre,
              fill_opacity=0.4
        ).add_to(a)


for _, row in list_max.iterrows():
    if row['geometry'] is not None:
        lat = row['geometry'].y
        lon = row['geometry'].x
        nombre = f"MAX: {int(row['secundcerc'])} secundarias y el nombre es {row['Nombre de SS.EE.']}"
        #nombre = 'Maximo: ' + row['secundcerc'].astype(str) + ' de Secundarias'
        
       
        fm.Circle(
              radius = 5000,
              fill=True,
              color="#25c22f",
              fill_color="#25c22f",
              location=[lat, lon],
              popup=nombre,
              fill_opacity=0.4
        ).add_to(a)

# Marcador con flecha personalizada (HTML/CSS)

lat_max = list_max['geometry'].y.values[0]
lon_max = list_max['geometry'].x.values[0]
fm.Marker(
    location=[lat_max, lon_max],
    icon=fm.Icon(color="green", icon="location-arrow", prefix="fa"),
    nombre = f"Nombre: {list_max['Nombre de SS.EE.'].values[0]} y tiene {int(list_max['secundcerc'].values[0])} secundarias",
    popup=nombre
).add_to(a)

lat_min = list_min['geometry'].y.values[0]
lon_min = list_min['geometry'].x.values[0]
fm.Marker(
    location=[lat_min, lon_min],
    icon=fm.Icon(color="red", icon="location-arrow", prefix="fa"),
    nombre = f"Nombre: {list_min['Nombre de SS.EE.'].values[0]} y tiene 0 secundarias",
    popup=nombre
).add_to(a)



# 3. Mostrar el mapa
a


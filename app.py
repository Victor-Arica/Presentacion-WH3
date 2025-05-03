import streamlit as st
from PIL import Image
import pandas as pd

st.title("Presentación de Datos Geoespaciales de escuelas en Perú")

# Crear pestañas
tabs = st.tabs(["Data Description", "Static Maps", "Dynamic Maps"])

with tabs[0]:
    st.header("Descripción de los Datos")
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

with tabs[1]:
    st.header("Mapas Estáticos")
    st.write("")


with tabs[2]:
    st.header("Mapas Dinámicos")
    st.write("Aquí puedes poner un mapa interactivo con `folium`, `pydeck`, etc.")

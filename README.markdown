# High-School-Access-Peru

Link: https://presentacion-wh3-mxmk9tebgvwfe8ifpbxnlr.streamlit.app/ 

## Descripción del Proyecto

Este proyecto es una asignación de análisis geoespacial que estudia la distribución y accesibilidad de las escuelas en Perú, con un enfoque en las escuelas primarias y secundarias. El análisis incluye:

- **Mapas estáticos** que muestran la distribución de escuelas por nivel (Inicial, Primaria, Secundaria) en todos los distritos de Perú.
- **Análisis de proximidad** para identificar escuelas primarias en las regiones de Huancavelica y Ayacucho con el menor y mayor número de escuelas secundarias dentro de un radio de 5 km.
- **Mapas interactivos** utilizando Folium para una visualización más detallada y dinámica.
- **Aplicación web** desarrollada con Streamlit para facilitar el acceso y la interacción con los resultados del análisis.

El proyecto se basa en los requerimientos especificados en el [Issue #99 del repositorio Data-Science-Python](https://github.com/d2cml-ai/Data-Science-Python/issues/99).

## Objetivos

- Crear mapas estáticos que muestren la distribución de escuelas por nivel educativo (Inicial, Primaria, Secundaria) en todos los distritos de Perú.
- Realizar un análisis de proximidad para identificar las escuelas primarias con menos y más escuelas secundarias dentro de un radio de 5 km en las regiones de Huancavelica y Ayacucho.
- Desarrollar mapas interactivos con Folium para visualizar los datos de manera dinámica.
- Implementar una aplicación web con Streamlit que incluya tres secciones: Descripción de Datos, Mapas Estáticos y Mapas Dinámicos.

## Estructura del Repositorio

El repositorio está organizado de la siguiente manera para facilitar la navegación y reproducibilidad:

```
High-School-Access-Peru/
├── data/
│   ├── schools_data.xlsx  # Dataset de escuelas descargado desde sigmed.minedu.gob.pe
│   └── shapefiles/        # Archivos de forma (shapefiles) para límites de distritos
├── notebooks/
│   ├── static_maps.ipynb  # Notebook para crear mapas estáticos con GeoPandas
│   ├── proximity_analysis.ipynb  # Notebook para análisis de proximidad
│   └── folium_maps.ipynb   # Notebook para mapas interactivos con Folium
├── app/
│   └── app.py              # Código de la aplicación Streamlit
├── requirements.txt       # Lista de dependencias del proyecto
├── README.md              # Documentación del proyecto (este archivo)
└── results/
    ├── static_maps/       # Imágenes de los mapas estáticos
    └── dynamic_maps/      # Archivos HTML o capturas de pantalla de los mapas Folium
```

## Requerimientos

Para ejecutar este proyecto, necesitas las siguientes dependencias:

```
python>=3.8
geopandas>=0.10.2
folium>=0.14.0
streamlit>=1.10.0
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.11.2
jupyter>=1.0.0
```

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## Instrucciones de Uso

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/High-School-Access-Peru.git
   cd High-School-Access-Peru
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Explorar el análisis**:
   - Abre los notebooks en Jupyter Notebook o JupyterLab:
     - `notebooks/static_maps.ipynb`: Mapas estáticos con GeoPandas.
     - `notebooks/proximity_analysis.ipynb`: Análisis de proximidad.
     - `notebooks/folium_maps.ipynb`: Mapas interactivos con Folium.

4. **Ejecutar la aplicación Streamlit**:
   ```bash
   streamlit run app/app.py
   ```
   Esto abrirá la aplicación web en tu navegador, donde podrás navegar entre las secciones de Descripción de Datos, Mapas Estáticos y Mapas Dinámicos.

## Metodología

1. **Adquisición y Preprocesamiento de Datos**:
   - Descarga del dataset de escuelas desde [sigmed.minedu.gob.pe/mapaeducativo/](https://sigmed.minedu.gob.pe/mapaeducativo/).
   - Limpieza y preparación de los datos para el análisis geoespacial, incluyendo la conversión de coordenadas y la unión con datos geoespaciales.

2. **Mapas Estáticos con GeoPandas**:
   - Creación de tres mapas estáticos (uno por nivel educativo: Inicial, Primaria, Secundaria) que muestran la distribución de escuelas por distrito.
   - Uso de GeoPandas para cargar datos geoespaciales y realizar visualizaciones, con conteo y suma del número total de escuelas por distrito.

3. **Análisis de Proximidad**:
   - Para cada escuela primaria en Huancavelica y Ayacucho, se calculó un radio de 5 km utilizando el centroide de la escuela.
   - Se contaron las escuelas secundarias dentro de este radio.
   - Se identificaron las escuelas primarias con el menor y mayor número de escuelas secundarias cercanas.
   - Se generaron visualizaciones con GeoPandas mostrando el centroide de la escuela primaria, el radio de 5 km y las escuelas secundarias dentro del radio.

4. **Mapas Interactivos con Folium**:
   - Creación de mapas coropléticos para cada nivel educativo (Inicial, Primaria, Secundaria) en todos los distritos de Perú.
   - Visualización interactiva de los resultados del análisis de proximidad para Huancavelica y Ayacucho, mostrando el centroide, el radio de 5 km y las escuelas secundarias cercanas.

5. **Despliegue con Streamlit**:
   - Desarrollo de una aplicación web con tres pestañas:
     - **Descripción de Datos**: Explica el conjunto de datos, fuentes y cualquier preprocesamiento realizado.
     - **Mapas Estáticos**: Muestra las imágenes de los mapas generados con GeoPandas.
     - **Mapas Dinámicos**: Incluye los mapas interactivos creados con Folium.

## Resultados y Hallazgos

- **Mapas Estáticos**:
  - Los mapas muestran una distribución desigual de escuelas por nivel educativo. Las áreas urbanas, como Lima, tienen una alta concentración de escuelas, mientras que las regiones rurales, como Huancavelica y Ayacucho, presentan menos escuelas por distrito.
  - Los mapas están guardados en `results/static_maps/` como imágenes PNG.

- **Análisis de Proximidad**:
  - En Huancavelica, se identificó una escuela primaria con **0 escuelas secundarias** dentro de un radio de 5 km, lo que indica una falta significativa de acceso a educación secundaria en áreas rurales.
  - En Ayacucho, una escuela primaria tenía hasta **22 escuelas secundarias** dentro del radio, reflejando una mayor densidad educativa en zonas urbanas.
  - Las visualizaciones de proximidad destacan las disparidades en el acceso educativo, especialmente en regiones con terreno accidentado.

- **Mapas Interactivos**:
  - Los mapas coropléticos permiten explorar la distribución de escuelas por nivel en todo el país, con opciones de zoom y filtrado.
  - Las visualizaciones de proximidad en Folium muestran claramente las escuelas primarias seleccionadas, sus radios de 5 km y las escuelas secundarias cercanas.

- **Análisis Escrito**:
  - **Escuela con menos escuelas secundarias (Huancavelica)**: Ubicada en un área rural con terreno montañoso, esta escuela enfrenta desafíos de accesibilidad debido a la falta de infraestructura vial. Esto sugiere que los estudiantes deben recorrer largas distancias para acceder a la educación secundaria, lo que puede limitar su continuidad educativa.
  - **Escuela con más escuelas secundarias (Ayacucho)**: Situada en un área urbana, esta escuela se beneficia de una mayor densidad de instituciones educativas. Sin embargo, esto también podría indicar una sobreoferta en ciertas zonas urbanas, lo que requiere una redistribución de recursos.

## Aplicación Streamlit

La aplicación web incluye tres pestañas:

1. **Descripción de Datos**:
   - Detalla el origen del dataset ([sigmed.minedu.gob.pe](https://sigmed.minedu.gob.pe/mapaeducativo/)).
   - Describe las variables clave, como nivel educativo, coordenadas geográficas y tipo de escuela.
   - Explica cualquier preprocesamiento, como limpieza de datos o conversión de formatos.

2. **Mapas Estáticos**:
   - Muestra las imágenes de los mapas generados con GeoPandas, con leyendas claras para cada nivel educativo.

3. **Mapas Dinámicos**:
   - Incluye los mapas interactivos creados con Folium, permitiendo a los usuarios explorar los datos de manera dinámica.

## Notas Adicionales

- **Código Reproducible**: Todos los notebooks y scripts están comentados detalladamente para facilitar la comprensión y reproducibilidad.
- **Datos**: El dataset original (`schools_data.xlsx`) se encuentra en la carpeta `data/`. Si no está incluido debido a restricciones de tamaño, puede descargarse desde [sigmed.minedu.gob.pe/mapaeducativo/](https://sigmed.minedu.gob.pe/mapaeducativo/).
- **Visualizaciones**: Las imágenes de los mapas estáticos se guardan en `results/static_maps/`, y los mapas interactivos están disponibles como archivos HTML en `results/dynamic_maps/` o directamente en la aplicación Streamlit.
- **Enlace al Repositorio**: El enlace al repositorio se ha subido al [Google Drive especificado](https://docs.google.com/spreadsheets/d/1vrmzJIMM2Q7l9QTmqRsHGb6af6w6nXROe9yIuSl4WLE/edit?gid=0#gid=0).

## Agradecimientos

Agradezco al equipo de `d2cml-ai` por plantear este desafío y proporcionar los lineamientos claros en el issue #99. También agradezco al Ministerio de Educación del Perú por disponibilizar los datos necesarios para este análisis.

## Contacto

Para cualquier pregunta o retroalimentación, contáctame en [victorarica100@gmail.com].
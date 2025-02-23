#Se requiere instalar estos completementos previos, verificar versiones en Requirements.txt
import os
import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import altair as alt # type: ignore
from vega_datasets import data # type: ignore

import numpy as np

from google_sheet_actions import GoogleSheetService

min_year = 2014
max_year = 2025

nombre = ''

google_connection = None
paises = None

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="DCC Dashboard 2025", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

#TITULO PRINCIPAL DEL DASHBOARD *******************
st.title('Departamento de Ciencias de la Computación - UCuenca')

#BARRA LATERAL
#st.subheader("Estadísticas personalizadas")
# Declaramos los parámetros en la barra lateral
with st.sidebar:
    # Filtro de Año de publicación
    file_name_gs = 'dash-dcc/dcc-pruebas-493a3b6215f3.json'
    google_sheet = 'DBDCC25'
    sheet_name = 'Publicaciones'

    google_connection = GoogleSheetService(file_name_gs, google_sheet, sheet_name)

    try:
        google_connection.name_columns = google_connection.read_column_names()
        columna_nombres = google_connection.name_columns.get('nombres').get('letra')
        rango_anios = st.slider("Selecciona un rango de años", min_year, max_year, (min_year, max_year))
    except Exception as e:
        st.error(f"Error al cargar nombres de columnas: {e}")

    sheet_name = 'Queries'
    name_column = google_connection.name_columns
    google_connection = GoogleSheetService(file_name_gs, google_sheet, sheet_name)
    google_connection.name_columns = name_column
    
    try:
        paises = google_connection.read_data_all_countries('Paises', 'B')
    except Exception as e:
        st.error(f"Error al cargar paises: {e}")

    try:
        nombres_maestros = google_connection.read_data_specific_columns(f"UNIQUE(Publicaciones!{columna_nombres}:{columna_nombres})", "SELECT Col1 WHERE Col1 <> ''")
        nombres_maestros = nombres_maestros['nombres'].tolist()
        nombres_maestros.insert(0, 'Todos')
        if 'Todos' in nombres_maestros:
            print("Index of 'Todos':", nombres_maestros.index('Todos'))
        else:
            st.warning("'Todos' no encontrado en la lista de nombres")
        nombre = st.selectbox("Selecciona un autor", nombres_maestros)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
    st.text("Base de datos externas")
    st.page_link("https://www.scopus.com/pages/organization/60072035", label="Scopus", icon="🌎")

# VISTA GENERAL DE LOS RESULTADOS **************

st.header('Estadísticas Generales')

# La idea es aquí en la lectura obtener el dataset desde una hoja de GoogleSheets, por ahora se ha hecho local...
# Cargamos el dataframe desde un CSV
# file_path = 'dash-dcc/DBDCC25.csv'
# if os.path.exists(file_path):
#     try:
#         dfDatos = pd.read_csv(file_path, sep=';', encoding='latin-1')
#         dfDatos['indexacion'] = dfDatos['indexacion'].replace(['', 'N/A', 'None', ' '], 'Por definir')  # Reemplazar valores
#     except Exception as e:
#         st.error(f"Error al leer el archivo: {e}")
# else:
#     st.error(f"Archivo no encontrado: {file_path}")

# PUBLICACIONES TOTALES

try:
    if nombre != "Todos":
        df_publicaciones_totales = google_connection.read_data_total_per_category('Publicaciones', rango_anios, nombre)
    else:
        df_publicaciones_totales = google_connection.read_data_total_per_category('Publicaciones', rango_anios, final_column='T')
    # google_connection.read_data_for_formula(f"=QUERY(COUNTUNIQUE(Publicaciones!A:A), \"SELECT *\")")
    print("df_publicaciones_totales", df_publicaciones_totales)
    st.metric("Publicaciones Totales", df_publicaciones_totales.iloc[0, 0])
except Exception as e:
    st.error(f"Error en Publicaciones Totales: {e}")
    
## GRAFICOS DE PASTEL    
def mostrar_grafico_pastel(google_connection, nombre, rango_anios, categoria_a_buscar, nombre_categoria, titulo_grafico, columna_final_contar_todo='T'):
    try:
        lista_columnas = ['codigo', categoria_a_buscar]
        if nombre != "Todos":
            lista_columnas.append('nombres')
            df_publicaciones_por_anio = google_connection.read_data_per_category('Publicaciones', lista_columnas, categoria_a_buscar, nombre_categoria, rango_anios, nombre)
        else:
            df_publicaciones_por_anio = google_connection.read_data_per_category('Publicaciones', lista_columnas, categoria_a_buscar, nombre_categoria, rango_anios, final_column=columna_final_contar_todo)
            
        print(df_publicaciones_por_anio)
        #grafica en pastel
        fig = px.pie(df_publicaciones_por_anio, names=nombre_categoria, values='CANTIDAD',
                          title=titulo_grafico)
        fig.update_layout(
            legend=dict(
                font=dict(size=10),  # Reduce tamaño para evitar que se corten
                orientation="v",  # Asegura que la leyenda sea vertical
                yanchor="top",
                y=1.02,
                xanchor="left",
                x=1.05
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error en Publicaciones por año: {e}")

def mostrar_grafico_barras(google_connection, nombre, rango_anios, categoria_a_buscar, nombre_categoria, titulo_grafico, columna_final_contar_todo='T'):
    try:
        lista_columnas = ['codigo', categoria_a_buscar]
        if nombre != "Todos":
            lista_columnas.append('nombres')
            df_publicaciones_por_anio = google_connection.read_data_per_category('Publicaciones', lista_columnas, categoria_a_buscar, nombre_categoria, rango_anios, nombre)
        else:
            df_publicaciones_por_anio = google_connection.read_data_per_category('Publicaciones', lista_columnas, categoria_a_buscar, nombre_categoria, rango_anios, final_column=columna_final_contar_todo)
            
        print(df_publicaciones_por_anio)
        #grafica en pastel
        fig = px.bar(df_publicaciones_por_anio, x=nombre_categoria, y='CANTIDAD',
                          title=titulo_grafico)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error en Publicaciones por año: {e}")
# PUBLICACIONES POR AÑO ----------------

# Llamada a la función

# TIPO DE PUBLICACIÓN ----------------
# # métricas en números
# publication_types = dfDatos["tipo_publicacion"].unique()
# for pub_type in publication_types:
#     count = len(dfDatos[dfDatos["tipo_publicacion"] == pub_type])
#     st.metric(f"Publications ({pub_type})", count)

# # Gráfico de pastel




# CLASIFICACION POR INDEXACION -----------------

# PENDIENTE ESTADÍSTICAS DE LOS PROYECTOS


#*********************************************************
#st.header(' ')
#Se añade una barra lateral que sirve para filtrar, se deberá establer búsquedas por periodos, autor, conferencias, paises,etc... (analizar con DCC)


# Mostramos las métricas
#dfAnoActual = dfDatos[dfDatos['anio_publicacion']==parAno]

# Declaramos 2 columnas en una proporción de 50% y 50%
mostrar_grafico_barras(google_connection, nombre, rango_anios, 'anio_publicacion', 'AÑO', 'Publicaciones por Año')
with st.container():
    c1,c2 = st.columns(2)
    with c1:    
        mostrar_grafico_pastel(google_connection, nombre, rango_anios, 'nombre', 'INDEXACIÓN', 'Publicaciones por Indexación', columna_final_contar_todo='Z')
        mostrar_grafico_pastel(google_connection, nombre, rango_anios, 'tipo_publicacion', 'TIPO PUBLICACIÓN', 'Publicaciones por Tipo de Publicación')
    with c2:
        mostrar_grafico_pastel(google_connection, nombre, rango_anios, 'nombre_area_frascati_amplio', 'ÁREA DE CONOCIMIENTO', 'Publicaciones por Área de Conocimiento')
        mostrar_grafico_pastel(google_connection, nombre, rango_anios, 'nombre_area_unesco_amplio', 'ÁREA DE CONOCIMIENTO UNESCO', 'Publicaciones por Área de Conocimiento UNESCO')

if nombre == "Todos":
    mostrar_grafico_barras(google_connection, nombre, rango_anios, 'nombres', 'AUTOR', 'Publicaciones por Autor', columna_final_contar_todo='AS')


#MAPA
def mostrar_mapa(df):
    print("Paises:", paises)
    
    df_full = paises.merge(df, on="COUNTRIES", how="left").fillna(0)
        
    url = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json'
    world_map_data = alt.topo_feature(url, 'countries')
    
    fig = alt.Chart(world_map_data).mark_geoshape().encode(
        color=alt.condition(
            alt.datum.CANTIDAD > 0,  # Si tiene datos, usa la escala de azules
            alt.Color('CANTIDAD:Q', scale=alt.Scale(scheme='bluegreen')),  
            alt.value('lightgray')  # Si no tiene datos, se muestra en gris
        ),
        tooltip=['COUNTRIES:N', 'CANTIDAD:Q']
    ).transform_lookup(
        lookup='properties.name',  
        from_=alt.LookupData(df_full, key='COUNTRIES', fields=['COUNTRIES', 'CANTIDAD'])
    ).project(
        type='naturalEarth1'
    ).properties(
        title='Distribución de Cantidad por País',
        width=600,
        height=400,
    ).configure_view(
        stroke='black'
    ).configure_title(
        fontSize=20
    )
    st.altair_chart(fig, use_container_width=True)

if nombre != "Todos":
    df_paises = google_connection.read_data_per_countries('Publicaciones', rango_anios, nombre)
    mostrar_mapa(df_paises)
    print(df_paises)
else:
    df_paises = google_connection.read_data_per_countries('Publicaciones', rango_anios, final_column='T')
    print(df_paises)
    mostrar_mapa(df_paises)

st.subheader("Más resultados...")

#Además Deberá existir una sección para Proyectos de Investigación y para Proyectos de Vinculación



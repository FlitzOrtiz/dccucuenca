import os
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import altair as alt  # type: ignore
from vega_datasets import data  # type: ignore
import numpy as np
from google_sheet_actions import GoogleSheetService

# Configuración inicial
MIN_YEAR = 2014
MAX_YEAR = 2025

st.set_page_config(
    page_title="DCC Dashboard 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Departamento de Ciencias de la Computación - UCuenca")

# Variables globales
google_connection = None
tipos_publicaciones = None
maestros = None
nombre = ""

# Barra lateral
with st.sidebar:
    file_name_gs = "dash-dcc/dcc-pruebas-493a3b6215f3.json"
    google_sheet = "DBDCC25"
    sheet_name = "Publicaciones"
    google_connection = GoogleSheetService(file_name_gs, google_sheet, sheet_name)
    
    try:
        rango_anios = st.slider("Selecciona un rango de años", MIN_YEAR, MAX_YEAR, (MIN_YEAR, MAX_YEAR))
    except Exception as e:
        st.error(f"Error al cargar nombres de columnas: {e}")
    
    try:
        departamentos = google_connection.get_unique_value_column("departamento")
        departamentos.remove("#N/A")
        
        def _select_all_departamentos():
            if "Todos" in st.session_state.selected_departamentos:
                st.session_state.selected_departamentos = ["Todos"]
                
        departamento = st.multiselect("Selecciona un departamento", departamentos, key="selected_departamentos", on_change=_select_all_departamentos, default=["Todos"])
    except Exception as e:
        st.error(f"Error al leer los departamentos: {e}")
    
    try:
        if "Todos" not in departamento:
            maestros = google_connection.get_professors_by_department(departamento)
        else:
            maestros = google_connection.get_unique_value_column("nombres")
            
        def _select_all_maestros():
            if "Todos" in st.session_state.selected_maestros:
                st.session_state.selected_maestros = ["Todos"]
                
        nombre = st.multiselect("Selecciona un autor", maestros, key="selected_maestros", on_change=_select_all_maestros, default=["Todos"])
    except Exception as e:
        st.error(f"Error al leer los maestros: {e}")
    
    st.text("Base de datos externas")
    st.page_link("https://www.scopus.com/pages/organization/60072035", label="Scopus", icon="🌎")

# Sección de estadísticas generales
st.header("Estadísticas Generales")

# Publicaciones totales
try:
    filtro = nombre if "Todos" not in nombre else maestros[1:]
    df_publicaciones_totales = google_connection.get_total_by_category("codigo", rango_anios, filtro)
    titulo_totales = f"Publicaciones Totales de {', '.join(filtro)}" if "Todos" not in nombre else "Publicaciones Totales"
    
    st.metric(titulo_totales, df_publicaciones_totales)
except Exception as e:
    st.error(f"Error en Publicaciones Totales: {e}")

# Función para gráficos

def mostrar_grafico(tipo, nombre, rango_anios, categoria, nombre_categoria, titulo_grafico):
    try:
        filtro = nombre if "Todos" not in nombre else maestros[1:]
        df_publicaciones = google_connection.get_data_by_category(categoria, rango_anios, filtro)
        
        if tipo == "pastel":
            fig = px.pie(df_publicaciones, names=categoria[0], values="CANTIDAD", title=titulo_grafico, labels={categoria[0]: nombre_categoria})
        else:
            fig = px.bar(df_publicaciones, x=categoria[0], y="CANTIDAD", title=titulo_grafico, labels={categoria[0]: nombre_categoria, "CANTIDAD": "Cantidad"}) 
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error en {nombre_categoria}: {e}")

# Función para mostrar mapa
def mostrar_mapa():
    if "Todos" in departamento:
        df_paises = google_connection.get_by_countries(tipo_publicacion, rango_anios, nombre)
    elif "Todos" in nombre:
        df_paises = google_connection.get_by_countries(tipo_publicacion, rango_anios, maestros[1:])
    else:
        df_paises = google_connection.get_by_countries(tipo_publicacion, rango_anios, nombre)
        
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
        from_=alt.LookupData(df_paises, key='COUNTRIES', fields=['COUNTRIES', 'CANTIDAD'])
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

# Mostrar gráficos
mostrar_grafico("barras", nombre, rango_anios, ["anio_publicacion"], "Año", "Publicaciones por Año")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        mostrar_grafico("pastel", nombre, rango_anios, ["nombre"], "INDEXACION", "Publicaciones por Indexación")
        mostrar_grafico("pastel", nombre, rango_anios, ["nombre_area_frascati_amplio"], "Área de Conocimiento", "Publicaciones por Área de Conocimiento")
    with c2:
        mostrar_grafico("pastel", nombre, rango_anios, ["tipo_publicacion"], "Tipo de Publicación", "Publicaciones por Tipo de Publicación")        
        mostrar_grafico("pastel", nombre, rango_anios, ["nombre_area_unesco_amplio"], "Área de Conocimiento UNESCO", "Publicaciones por Área de Conocimiento UNESCO")
    
    mostrar_grafico("barras", nombre, rango_anios, ["nombres"], "Autor", "Publicaciones por Autor")

# Mostrar mapa
try:
    tipos_publicaciones = google_connection.get_unique_value_column("tipo_publicacion")
    
    def _selected_all_tipos():
        if "Todos" in st.session_state.selected_tipos:
            st.session_state.selected_tipos = ["Todos"]
    
    tipo_publicacion = st.multiselect("Selecciona un tipo de publicación", tipos_publicaciones, key="selected_tipos", on_change=_selected_all_tipos, default=["Todos"])
except Exception as e:
    st.error(f"Error al leer los tipos de publicaciones: {e}")

# Muestra el mapa
mostrar_mapa()

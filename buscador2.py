import streamlit as st
import pandas as pd

# ID del archivo Excel en Google Drive
file_id = "1hqbyLewjweB4uOCrnRYcVTdpSHCQN3WQ"

# URL de descarga directa de Google Drive
excel_url = f"https://drive.google.com/uc?export=download&id={file_id}"

# Cargar datos en caché para mejorar rendimiento
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel(excel_url, sheet_name="Buscar", engine="openpyxl")

        # Verificar que hay suficientes filas antes de procesar
        if len(df) < 4:
            return None

        # Usar la fila 4 como encabezado y eliminar las tres primeras filas
        df.columns = df.iloc[3]  # La fila 4 contiene los nombres de las columnas
        df = df[4:].reset_index(drop=True)  # Omitir las tres primeras filas

        # Convertir todas las columnas a string para acelerar la búsqueda
        df = df.astype(str).fillna("")

        # Renombrar columnas específicas si existen
        nombres_deseados = ["Producto", "Marca", "Precio"]
        for i, nombre in enumerate(nombres_deseados):
            if i < len(df.columns):
                df.rename(columns={df.columns[i]: nombre}, inplace=True)

        return df

    except Exception as e:
        st.error(f"⚠️ Error al cargar el archivo Excel: {e}")
        return None

df = cargar_datos()
if df is None:
    st.stop()

# Interfaz en Streamlit
st.title("📦 Buscador de Productos")

# Espacio para la búsqueda con botón
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input("🔎 Buscar producto:", key="query_input")

with col2:
    buscar = st.button("🔍 Buscar")

# Aplicar búsqueda solo si se presiona el botón
if buscar and query:
    mask = df.apply(lambda row: row.str.contains(query, case=False, na=False)).any(axis=1)
    df_filtrado = df[mask]
else:
    df_filtrado = df

# Mostrar la tabla optimizada
st.data_editor(df_filtrado, height=600, use_container_width=True)

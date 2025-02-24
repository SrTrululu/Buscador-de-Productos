import streamlit as st
import pandas as pd
from streamlit_extras.app_refresh import st_autorefresh  # 👈 Para refrescar automáticamente

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

# 🚀 Recargar la app automáticamente cada 500ms (0.5 segundos) 👇
st_autorefresh(interval=500, key="refresh")

# Barra de búsqueda (se actualiza sin Enter ni clics)
query = st.text_input("🔎 Buscar producto:", value=st.session_state.get("query", ""))

# Guardar la búsqueda en session_state
st.session_state["query"] = query

# Aplicar búsqueda solo si hay texto
if query:
    # Filtrar con método vectorizado (más rápido que apply)
    mask = df.apply(lambda row: row.str.contains(query, case=False, na=False)).any(axis=1)
    df_filtrado = df[mask]
else:
    df_filtrado = df

# Mostrar la tabla optimizada
st.data_editor(df_filtrado, height=600, use_container_width=True)

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

        # Manejo de nombres de columnas
        columnas_unicas = []
        columnas_procesadas = set()
        for i, col in enumerate(df.columns):
            if pd.isna(col) or col.strip() == "" or col in columnas_procesadas:
                nuevo_nombre = f"Columna_{i}"
            else:
                nuevo_nombre = col.strip()
                columnas_procesadas.add(nuevo_nombre)
            columnas_unicas.append(nuevo_nombre)

        df.columns = columnas_unicas  # Asignar los nuevos nombres de columna

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

# Inicializar estado de búsqueda
if "query" not in st.session_state:
    st.session_state.query = ""

# Barra de búsqueda (se actualiza sin presionar Enter)
query = st.text_input("🔎 Buscar producto:", value=st.session_state.query)

# Filtrar solo si hay texto en la búsqueda
if query:
    df_filtrado = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
else:
    df_filtrado = df

# Actualizar la búsqueda en session_state sin necesidad de callbacks
st.session_state.query = query

# Mostrar la tabla con más espacio
st.data_editor(df_filtrado, height=600, use_container_width=True)

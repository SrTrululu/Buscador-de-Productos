import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
import json

# Cargar credenciales desde una variable de entorno
gcp_credentials = os.getenv("GCP_CREDENTIALS")
if gcp_credentials:
    creds_dict = json.loads(gcp_credentials)
    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    cliente = gspread.authorize(creds)
else:
    st.error("⚠️ No se encontraron credenciales de Google Cloud. Asegúrate de configurarlas correctamente.")
    st.stop()

# Abre el Google Sheets por su ID
spreadsheet_id = "1znQhorwDGB2YPlIF05pDqkwsC6dO8UB23vwVENjdBXQ"
hoja = cliente.open_by_key(spreadsheet_id)

# Accede a una pestaña específica
worksheet = hoja.worksheet("Buscar")
datos = worksheet.get_all_values()

# Verificar que hay suficientes filas antes de procesar
if len(datos) < 4:
    st.error("⚠️ No hay suficientes datos en la hoja de cálculo.")
    st.stop()

# Usar la fila 4 como encabezado y eliminar las tres primeras filas
columnas = datos[3]  # La fila 4 contiene los nombres de las columnas
datos_limpios = datos[4:]  # Omitir las tres primeras filas vacías

# Eliminar columnas vacías y manejar nombres duplicados
columnas_unicas = []
columnas_procesadas = set()
for i, col in enumerate(columnas):
    if col.strip() == "" or col in columnas_procesadas:
        nuevo_nombre = f"Columna_{i}"
    else:
        nuevo_nombre = col.strip()
        columnas_procesadas.add(nuevo_nombre)
    columnas_unicas.append(nuevo_nombre)

# Convertir a DataFrame
df = pd.DataFrame(datos_limpios, columns=columnas_unicas)

# Renombrar columnas específicas si existen
nombres_deseados = ["Producto", "Marca", "Precio"]
for i, nombre in enumerate(nombres_deseados):
    if i < len(df.columns):
        df.rename(columns={df.columns[i]: nombre}, inplace=True)

# Interfaz en Streamlit
st.title("📦 Buscador de Productos")

# Barra de búsqueda
query = st.text_input("🔎 Buscar producto:")

# Filtrar los datos si hay una búsqueda
df_filtrado = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)] if query else df

# Mostrar la tabla con más espacio
st.data_editor(df_filtrado, height=600, use_container_width=True)
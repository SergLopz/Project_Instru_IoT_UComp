import streamlit as pd
import streamlit as st
import numpy as np
import pandas as pd

# 1. Configuración de la página del Dashboard
st.set_page_config(
    page_title="Dashboard Interactivo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Mi Dashboard Interactivo")
st.markdown("Ejemplo de control de estado y visualización de datos en tiempo real.")

# 2. SECCIÓN: Control de Estado (On / Off)
st.subheader("⚙️ Control de Estado")

# Opción A: Usando un Toggle (Switch) - Recomendado por estética
switch_activo = st.toggle("Cambiar estado con Switch")
estado_switch = "**ON**" if switch_activo else "**OFF**"
st.write(f"El estado actual del Switch es: {estado_switch}")

st.divider() # Línea divisoria

# Opción B: Usando un Botón Clásico (Mantiene el estado en la sesión)
if 'boton_on' not in st.session_state:
    st.session_state.boton_on = False

if st.button("Alternar estado con Botón"):
    st.session_state.boton_on = not st.session_state.boton_on

estado_boton = "**ON**" if st.session_state.boton_on else "**OFF**"
st.write(f"El estado actual del Botón es: {estado_boton}")


# 3. SECCIÓN: Dashboard Interactivo (Métricas y Gráficos)
st.divider()
st.subheader("📈 Métricas del Negocio")

# Filtro interactivo en la barra lateral que afecta al dashboard
st.sidebar.header("Filtros del Dashboard")
multiplicador = st.sidebar.slider("Multiplicador de Datos", 1.0, 5.0, 1.0)

# Generación de datos ficticios basados en el filtro
chart_data = pd.DataFrame(
    np.random.randn(20, 3) * multiplicador,
    columns=['Ventas', 'Ganancias', 'Costos']
)

# Renderizado de métricas en columnas
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Totales", f"${chart_data['Ventas'].sum():.2f}", "+12%")
col2.metric("Ganancias", f"${chart_data['Ganancias'].sum():.2f}", "-4%")
col3.metric("Estado del Sistema", "Activo" if switch_activo else "Inactivo")

# Gráfico interactivo
st.line_chart(chart_data)
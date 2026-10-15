import streamlit as st
import pandas as pd
import numpy as np
import paho.mqtt.client as mqtt
from datetime import datetime
import time

# ==========================================
# CONFIGURACIÓN GENERAL Y CONSTANTES
# ==========================================
MQTT_BROKER = "192.168.1.100"  # ⚠️ REEMPLAZA CON LA IP DE TU ESP32
MQTT_PORT = 1883

TOPICS = [
    "habitacion/ventana/temperatura",
    "habitacion/ventana/humedad",
    "habitacion/ventana/luz_estado",
    "habitacion/puerta/estado",
    "casa/led"
]

st.set_page_config(page_title="Dashboard IoT Domótica", layout="wide", page_icon="🏠")

# ==========================================
# INICIALIZACIÓN DEL ESTADO DE SESIÓN (BUFFER DE DATOS)
# ==========================================
if "mqtt_connected" not in st.session_state:
    st.session_state.mqtt_connected = False

# Creamos un diccionario para almacenar el último valor conocido de cada tópico
if "live_data" not in st.session_state:
    st.session_state.live_data = {topic: "Esperando datos..." for topic in TOPICS}

# Guardamos un histórico para Pandas/NumPy (Filtrado por tiempo)
if "historical_data" not in st.session_state:
    st.session_state.historical_data = []

# ==========================================
# CALLBACKS DE PAHO-MQTT
# ==========================================
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        st.session_state.mqtt_connected = True
        for topic in TOPICS:
            client.subscribe(topic)
    else:
        st.session_state.mqtt_connected = False

def on_message(client, userdata, msg):
    payload_str = msg.payload.decode("utf-8")
    topic = msg.topic
    
    # Actualizar valor en tiempo real
    st.session_state.live_data[topic] = payload_str
    
    # Guardar en el histórico si son datos numéricos (temperatura/humedad)
    if "temperatura" in topic or "humedad" in topic:
        try:
            val = float(payload_str)
            st.session_state.historical_data.append({
                "timestamp": datetime.now(),
                "topic": topic.split("/")[-1], # Guarda solo 'temperatura' o 'humedad'
                "valor": val
            })
            # Mantener el histórico limitado a los últimos 200 registros para no saturar memoria
            if len(st.session_state.historical_data) > 200:
                st.session_state.historical_data.pop(0)
        except ValueError:
            pass

# ==========================================
# GESTIÓN DE CONEXIÓN MQTT PERSISTENTE
# ==========================================
@st.cache_resource
def get_mqtt_client():
    # paho-mqtt v2 requiere declarar expresamente la API de callback
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start() # Inicia el hilo en segundo plano
    except Exception as e:
        st.error(f"No se pudo conectar al Broker ESP32 en {MQTT_BROKER}: {e}")
    return client

# Inicializamos el cliente (gracias a cache_resource solo se ejecuta una vez)
mqtt_client = get_mqtt_client()

# ==========================================
# RENDERIZADO DE LA INTERFAZ WEB (STREAMLIT)
# ==========================================
st.title("🏠 Panel de Control IoT - ESP32 PicoMQTT")

# Barra Superior de Estado del Broker
status_color = "🔴" if not st.session_state.mqtt_connected else "🟢"
led_casa = st.session_state.live_data["casa/led"]
st.subheader(f"{status_color} Estado del Broker: {'Conectado' if st.session_state.mqtt_connected else 'Desconectado'}")
st.caption(f"Último latido recibido en `casa/led`: **{led_casa}**")

st.divider()

# Sección de Tarjetas en Tiempo Real (Métricas)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🪟 Nodo G1: Ventana")
    temp = st.session_state.live_data["habitacion/ventana/temperatura"]
    hum = st.session_state.live_data["habitacion/ventana/humedad"]
    luz = st.session_state.live_data["habitacion/ventana/luz_estado"]
    
    c_temp, c_hum, c_luz = st.columns(3)
    c_temp.metric("Temperatura", f"{temp} °C" if "Esperando" not in temp else temp)
    c_hum.metric("Humedad", f"{hum} %" if "Esperando" not in hum else hum)
    c_luz.metric("Luz Estado", luz)

with col2:
    st.markdown("### 🚪 Nodo G2: Puerta")
    puerta_estado = st.session_state.live_data["habitacion/puerta/estado"]
    
    # Un formato condicional visual simple
    if puerta_estado.lower() in ["abierta", "open", "1"]:
        st.error(f"🚨 LA PUERTA ESTÁ: {puerta_estado.upper()}")
    elif puerta_estado.lower() in ["cerrada", "closed", "0"]:
        st.success(f"🔒 LA PUERTA ESTÁ: {puerta_estado.upper()}")
    else:
        st.info(f"ℹ️ Estado puerta: {puerta_estado}")

st.divider()

# Sección Analítica (Pandas / NumPy / Gráficos)
st.markdown("### 📊 Historial Analítico de Variables")

if st.session_state.historical_data:
    # Convertimos la lista de diccionarios en un DataFrame de Pandas
    df = pd.DataFrame(st.session_state.historical_data)
    
    # Estructuramos el DataFrame para graficar fácilmente usando Pandas (Pivot table)
    df_pivot = df.pivot_table(index="timestamp", columns="topic", values="valor")
    
    # Procesamiento matemático básico con NumPy si existen datos
    if not df_pivot.empty:
        col_an1, col_an2 = st.columns(2)
        
        with col_an1:
            st.write("**Gráfico de Tendencia**")
            st.line_chart(df_pivot)
            
        with col_an2:
            st.write("**Resumen Estadístico (NumPy/Pandas)**")
            st.dataframe(df_pivot.describe())
else:
    st.info("Esperando que ingresen suficientes datos numéricos para procesar gráficos estadísticos...")

# Mecanismo de autorefresco automático cada 2 segundos para actualizar el dashboard
time.sleep(2)
st.rerun()

# uv add streamlit pandas numpy paho-mqtt
# uv run streamlit run app.py

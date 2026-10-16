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

st.set_page_config(page_title="Dashboard IoT Pro", layout="wide", page_icon="🏠")

# ==========================================
# ESTILOS CSS PERSONALIZADOS (Para tarjetas e iconos)
# ==========================================
st.markdown("""
<style>
    .card-sensor {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 10px;
    }
    .card-icon {
        font-size: 2.5rem;
    }
    .card-data h4 {
        margin: 0;
        color: #94A3B8;
        font-size: 0.9rem;
    }
    .card-data p {
        margin: 0;
        font-size: 1.8rem;
        font-weight: bold;
        color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DEL ESTADO DE SESIÓN
# ==========================================
if "mqtt_connected" not in st.session_state:
    st.session_state.mqtt_connected = False

if "live_data" not in st.session_state:
    st.session_state.live_data = {topic: "Esperando..." for topic in TOPICS}

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
    payload_str = msg.payload.decode("utf-8").strip()
    topic = msg.topic
    st.session_state.live_data[topic] = payload_str
    
    if "temperatura" in topic or "humedad" in topic:
        try:
            val = float(payload_str)
            st.session_state.historical_data.append({
                "timestamp": datetime.now(),
                "topic": topic.split("/")[-1],
                "valor": val
            })
            if len(st.session_state.historical_data) > 200:
                st.session_state.historical_data.pop(0)
        except ValueError:
            pass

# ==========================================
# GESTIÓN DE CONEXIÓN MQTT
# ==========================================
@st.cache_resource
def get_mqtt_client():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        pass
    return client

mqtt_client = get_mqtt_client()

# Lógica para enviar comandos al ESP32
def publicar_comando(topic, payload):
    if st.session_state.mqtt_connected:
        mqtt_client.publish(topic, payload, qos=1)
    else:
        st.warning("⚠️ No se puede enviar: Broker desconectado.")

# ==========================================
# DISEÑO DE LA INTERFAZ (SIDEBAR / BARRA LATERAL)
# ==========================================
with st.sidebar:
    st.header("🎛️ Panel de Control")
    
    # Estado de la conexión con badge visual
    if st.session_state.mqtt_connected:
        st.success("🟢 Broker Online")
    else:
        st.error("🔴 Broker Offline")
        st.info("Nota: La web mostrará marcadores de posición hasta que el ESP32 se encienda.")

    st.divider()
    st.subheader("💡 Actuador Remoto")
    st.caption("Control de `casa/led`")
    
    # Switch interactivo para encender/apagar el LED remoto
    led_actual = st.session_state.live_data["casa/led"]
    # Determinamos el estado inicial del switch basado en lo que dice el broker
    estado_inicial = True if led_actual == "1" else False
    
    btn_led = st.toggle("Estado del LED de la Casa", value=estado_inicial)
    
    # Si el usuario interactúa, publicamos el cambio inmediatamente
    if "prev_btn_led" not in st.session_state:
        st.session_state.prev_btn_led = btn_led

    if btn_led != st.session_state.prev_btn_led:
        payload_a_enviar = "1" if btn_led else "0"
        publicar_comando("casa/led", payload_a_enviar)
        st.session_state.prev_btn_led = btn_led
        st.toast(f"Comando enviado: {payload_a_enviar} a casa/led")

# ==========================================
# CUERPO PRINCIPAL DEL DASHBOARD
# ==========================================
st.title("🏠 Panel de Control IoT - ESP32 PicoMQTT")
st.divider()

# Fila superior de Tarjetas Personalizadas con HTML/Emojis (Sustitutos óptimos y ligeros de SVG)
col_temp, col_hum, col_luz = st.columns(3)

# 1. Tarjeta de Temperatura
with col_temp:
    t_val = st.session_state.live_data["habitacion/ventana/temperatura"]
    t_text = f"{t_val} °C" if "Esperando" not in t_val else t_val
    st.markdown(f"""
    <div class="card-sensor">
        <div class="card-icon">🌡️</div>
        <div class="card-data">
            <h4>Temperatura</h4>
            <p>{t_text}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 2. Tarjeta de Humedad
with col_hum:
    h_val = st.session_state.live_data["habitacion/ventana/humidity" if "humidity" in st.session_state.live_data else "habitacion/ventana/humedad"]
    h_text = f"{h_val} %" if "Esperando" not in h_val else h_val
    st.markdown(f"""
    <div class="card-sensor">
        <div class="card-icon">💧</div>
        <div class="card-data">
            <h4>Humedad</h4>
            <p>{h_text}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 3. Tarjeta Dinámica de Luz (Maneja los 3 estados parametrizados por el LDR)
with col_luz:
    luz_payload = st.session_state.live_data["habitacion/ventana/luz_estado"].lower().strip()
    
    # Evaluación de estados dinámicos del LDR con iconos adaptativos
    if "soleado" in luz_payload or luz_payload == "2":
        icon_luz = "☀️"
        estado_luz = "Soleado"
    elif "nublado" in luz_payload or luz_payload == "1":
        icon_luz = "☁️"
        estado_luz = "Nublado"
    elif "noche" in luz_payload or luz_payload == "0":
        icon_luz = "🌙"
        estado_luz = "De Noche"
    else:
        icon_luz = "🔍"
        estado_luz = st.session_state.live_data["habitacion/ventana/luz_estado"]

    st.markdown(f"""
    <div class="card-sensor">
        <div class="card-icon">{icon_luz}</div>
        <div class="card-data">
            <h4>Ambiente (LDR)</h4>
            <p>{estado_luz}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Segunda Sección: Estado de la Puerta
st.markdown("### 🚪 Estado de Acceso")
puerta_estado = st.session_state.live_data["habitacion/puerta/estado"]

if puerta_estado.lower() in ["abierta", "open", "1"]:
    st.error(f"🚨 ALERT: La puerta de la habitación está ABIERTA")
elif puerta_estado.lower() in ["cerrada", "closed", "0"]:
    st.success(f"🔒 SEGURIDAD: La puerta de la habitación está CERRADA")
else:
    st.info(f"ℹ️ Estado de la puerta: {puerta_estado}")

st.divider()

# Tercera Sección: Gráficos de tendencias históricos (Pandas / NumPy)
st.markdown("### 📊 Historial de Telemetría")
if st.session_state.historical_data:
    df = pd.DataFrame(st.session_state.historical_data)
    df_pivot = df.pivot_table(index="timestamp", columns="topic", values="valor")
    
    if not df_pivot.empty:
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            st.line_chart(df_pivot)
        with col_g2:
            st.dataframe(df_pivot.describe())
else:
    st.info("Los gráficos estadísticos aparecerán cuando el ESP32 publique lecturas numéricas recurrentes.")

# Forzar el refresco de la UI cada 2 segundos
time.sleep(2)
st.rerun()


# uv add streamlit pandas numpy paho-mqtt
# uv run streamlit run app.py

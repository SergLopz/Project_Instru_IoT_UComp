# 📡 Sistema de Monitoreo IoT para Ambientes Controlados

**Versión: 0.1**

## 📋 Descripción del Proyecto

Este proyecto consiste en un sistema de monitoreo IoT distribuido para la captura, transmisión y visualización en tiempo real de variables ambientales y de seguridad (temperatura, humedad, iluminación y detección de apertura de puertas). 

La arquitectura utiliza un esquema de red híbrido (**ESP-NOW + Wi-Fi/MQTT**), donde nodos sensores de bajo consumo procesan la información de manera remota y la transmiten a un nodo concentrador central, el cual alimenta un broker MQTT en un entorno local y un dashboard web interactivo.

---

## 🛠️ Arquitectura y Componentes

### 1. Hardware y Microcontroladores
* **Nodo Central (Gateway):** ESP32 DevKit v1 (WROOM)
  * *Función:* Receptor ESP-NOW, cliente MQTT vía Wi-Fi.
* **Nodos Remotos (Sensores x3):** ESP32-C3 Super Mini
  * *Función:* Lectura de sensores y transmisión de bajo consumo vía ESP-NOW.
* **Sensores Utilizados:**
  * **KY-015:** Temperatura y Humedad relativa (DHT11).
  * **KY-018:** LDR / Fotorresistencia (Nivel de iluminación).
  * **KY-003:** Sensor de Efecto Hall (Apertura/Cierre de puertas).

### 2. Software e Infraestructura
* **Firmware:** MicroPython (administrado localmente mediante Thonny IDE).
* **Entorno del Proyecto:** Administrado con **`uv`** (`pyproject.toml`, `uv.lock`).
* **Broker MQTT:** Eclipse Mosquitto desplegado en contenedor **Docker** (`homelab/`).
* **Dashboard Web:** Aplicación web en tiempo real construida con **Streamlit** y **Plotly** (`web_app/`).

---

## 📂 Estructura del Repositorio

```text
Project_Instru_IoT_UComp/
├── documents/            # Documentación técnica y propuesta del proyecto
├── firmware/             # Código fuente en MicroPython para los microcontroladores
│   ├── nod_c3/           # Firmware modular y config para nodos ESP32-C3
│   └── nod_central/      # Firmware del Gateway ESP32 WROOM (ESP-NOW -> MQTT)
├── homelab/              # Infraestructura Docker (docker-compose.yml, mosquitto.conf)
├── web_app/              # Dashboard interactivo en Streamlit (app.py, mqtt_client.py)
├── .gitignore            # Exclusión de entornos virtuales, temporales y datos
├── pyproject.toml        # Declaración de dependencias del proyecto (uv)
├── uv.lock               # Registro exacto de versiones para reproducibilidad
└── README.md             # Documentación principal del proyecto
```
---
## 📝 Notas de versión

### Versión 0.1
Guía inicial de organización, arquitectura y estructuración del repositorio enfocado al desarrollo de sistemas IoT multinodales.

*Nota: Esta versión inicial se encuentra en desarrollo y cuenta con el apoyo de herramientas de Inteligencia Artificial para la estructuración y documentación del proyecto.*
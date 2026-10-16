# 📡 Sistema de Monitoreo IoT para Ambientes Controlados

**Versión: 0.2**

## 📋 Descripción del Proyecto

Este proyecto consiste en un sistema de monitoreo IoT distribuido para la captura, transmisión y visualización en tiempo real de variables ambientales y de seguridad (temperatura, humedad, iluminación y detección de apertura de puertas). 

La arquitectura utiliza un esquema de red híbrido (**ESP-NOW + Wi-Fi/MQTT**), donde nodos sensores de bajo consumo procesan la información de manera remota y la transmiten a un nodo concentrador central, el cual alimenta un broker MQTT en un entorno local y un dashboard web interactivo.

---

## 🛠️ Arquitectura y Componentes

### 1. Hardware y Microcontroladores
* **Nodo Central (Broker):** ESP32 DevKit v1 (WROOM)
  * *Función:* Receptor, Broker MQTT vía Wi-Fi.
* **Nodos Remotos (g1 & g2):** ESP32 DevKit v1 (WROOM)
  * *Función:* Lectura de sensores y transmisión bajo PubSUbClient en la red Wi-Fi.
* **Sensores Utilizados:**
  * **KY-015:** Temperatura y Humedad relativa.
  * **KY-018:** LDR / Fotorresistencia.
  * **KY-003:** Sensor de Efecto Hall.
  * **KY-032:** Sensor de Obstaculos.

### 2. Software e Infraestructura
* **Firmware:** C++ / Sketch de Arduino (compilado y subido con Arduino IDE).
* **Entorno del Proyecto:** Administrado con **`uv`** (`pyproject.toml`, `uv.lock`).
* **Broker MQTT:** Una placa ESP32 con la libreria *PicoMQTT*.
* **Dashboard Web:** Aplicación web en tiempo real construida con **Streamlit** y **Plotly** (`web_app/`).

---

## 📂 Estructura del Repositorio

```text
Project_Instru_IoT_UComp/
├── documents/             # Documentación técnica y propuesta del proyecto
├── firmware/              # Código fuente en MicroPython para los microcontroladores
│   ├── g1_ventana/        # Firmware modular con config para  el nodo de la ventana
│   ├── g2_puerta/         # Firmware modular con config para  el nodo de la puerta
│   └── broker_MQTT_ESP32/ # Firmware del Gateway ESP32 WROOM (ESP-NOW -> MQTT)
├── homelab/               # Infraestructura Docker (docker-compose.yml, mosquitto.conf)
├── web_app/               # Dashboard interactivo en Streamlit (app.py, mqtt_client.py)
├── .gitignore             # Exclusión de entornos virtuales, temporales y datos
├── pyproject.toml         # Declaración de dependencias del proyecto (uv)
├── uv.lock                # Registro exacto de versiones para reproducibilidad
└── README.md              # Documentación principal del proyecto
```
---
## 📝 Notas de versión

### Versión 0.1
Guía inicial de organización, arquitectura y estructuración del repositorio enfocado al desarrollo de sistemas IoT multinodales.

### Versión 0.2
Para comodidad y disponibilidad se cambia el entorno a Arduino IDE, con el fin de utilizar librerías como lo es *PicoMQTT*.

*Nota: Esta versión inicial se encuentra en desarrollo y cuenta con el apoyo de herramientas de Inteligencia Artificial para la estructuración y documentación del proyecto.*
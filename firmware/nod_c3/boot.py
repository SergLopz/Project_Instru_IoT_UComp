# boot.py - ESP32-C3 Super Mini
import gc
import esp

# Desactivar mensajes de depuración del kernel de Espressif
esp.osdebug(None)

# Limpieza inicial de memoria RAM
gc.collect()

print("--- ESP32-C3 Super Mini: boot.py ejecutado ---")
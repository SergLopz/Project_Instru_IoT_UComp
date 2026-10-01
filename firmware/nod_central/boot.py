# boot.py - Ejecutado al arrancar el sistema
import gc
import esp

# Desactivar mensajes de depuración del kernel del ESP32
esp.osdebug(None)

# Ejecutar el recolector de basura para optimizar la memoria RAM
gc.collect()

print("--- ESP32: boot.py ejecutado correctamente ---")
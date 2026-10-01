# main.py - Prueba de Blink y Salida Segura en ESP32-C3 Super Mini
import machine
import time

# 1. Configuración del LED integrado de la ESP32-C3 (GPIO8)
led = machine.Pin(8, machine.Pin.OUT)

# 2. Configuración del Pin de Emergencia (GPIO4 con Pull-Up interno)
# Para detener la ejecución: Conecta un jumper de GPIO4 a GND.
pin_stop = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

#==================================================")
#--- ESP32-C3 Super Mini: Prueba de Blink ---")
#Para detener y volver a la consola (>>>):")
#  a) Presiona Ctrl + C en la consola de Thonny.")
#  b) Puentea el GPIO4 a GND (Tierra).")
#==================================================\n")

# Función auxiliar para controlar el LED (Active LOW: 0 encendido, 1 apagado)
def apagar_led():
    led.value(1)

def encender_led():
    led.value(0)

# Aseguramos estado inicial apagado
apagar_led()

try:
    contador = 0
    while True:
        # --- VERIFICACIÓN DE EMERGENCIA POR HARDWARE (GPIO4 a GND) ---
        if pin_stop.value() == 0:
            print("\n[ALERTA] ¡Se detectó conexión a GND en GPIO5!")
            print("[INFO] Saliendo del bucle y volviendo a REPL (>>>)...")
            apagar_led()
            break  # Rompe el bucle while True

        # --- LÓGICA DEL BLINK ---
        encender_led()
        print(f"[{contador}] LED Encendido (GPIO8 = 0)")
        time.sleep_ms(500)  # Pausa para permitir interrupciones serie

        # Segunda verificación del pin de emergencia antes del siguiente ciclo
        if pin_stop.value() == 0:
            print("\n[ALERTA] ¡Se detectó conexión a GND en GPIO4!")
            apagar_led()
            break

        apagar_led()
        print(f"[{contador}] LED Apagado (GPIO8 = 1)")
        time.sleep_ms(500)

        contador += 1

except KeyboardInterrupt:
    # Captura Ctrl + C o el botón STOP en Thonny
    print("\n[INFO] Ejecución interrumpida mediante Ctrl + C / STOP.")

finally:
    # Este bloque siempre apaga el LED al salir del programa
    apagar_led()
    print("\n--- Programa finalizado. Modo REPL listo (>>>) ---")

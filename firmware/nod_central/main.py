# main.py - Prueba de Blink con mecanismo de salida segura
import machine
import time

# 1. Configuración del LED integrado (GPIO2 en ESP32 DevKit V1)
led = machine.Pin(2, machine.Pin.OUT)

# 2. Configuración del Pin de Emergencia / Parada
# Usamos el GPIO4 con PULL_UP interna (el pin estará normalmente en HIGH/1).
# Para activar la parada, basta con conectar un jumper del GPIO4 a GND (LOW/0).
pin_stop = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

#==================================================
#--- ESP32 DevKit V1: Prueba de Blink Iniciada ---
#Para detener y volver a la consola (>>>):
#  a) Presiona Ctrl + C en la consola REPL.
#  b) Puentea el GPIO4 a GND (Tierra).
#==================================================

try:
    contador = 0
    while True:
        # --- VERIFICACIÓN DE EMERGENCIA POR HARDWARE (GPIO4 a GND) ---
        if pin_stop.value() == 0:
            print("\n[ALERTA] ¡Se detectó conexión a GND en GPIO4!")
            print("[INFO] Saliendo del bucle y volviendo a REPL (>>>)...")
            led.value(0) # Apagar LED antes de salir
            break        # Rompe el bucle while True

        # --- LÓGICA DEL BLINK ---
        led.value(1)
        print(f"[{contador}] LED Encendido")
        time.sleep_ms(1000)  # Pausa de 500ms (Permite atender comunicaciones serie)

        # Volvemos a verificar el pin antes de la segunda pausa
        if pin_stop.value() == 0:
            print("\n[ALERTA] ¡Se detectó conexión a GND en GPIO4!")
            break

        led.value(0)
        print(f"[{contador}] LED Apagado")
        time.sleep_ms(1000)

        contador += 1

except KeyboardInterrupt:
    # Captura Ctrl + C enviado desde Pymakr / VS Code / Thonny
    print("\n[INFO] Ejecución interrumpida mediante Ctrl + C desde la consola.")

finally:
    # Este bloque siempre se ejecuta al salir del bucle
    led.value(0)
    print("\n--- Programa finalizado. Modo REPL interactivo listo (>>>) ---")

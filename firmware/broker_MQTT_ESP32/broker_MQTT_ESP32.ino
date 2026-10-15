/**
 * @file broker_mqtt.ino
 * @brief ESP32 como Cliente Wi-Fi y Broker MQTT Local con control de LED integrado
 * Librería requerida: picoMQTT
 */

#include <WiFi.h>
#include <PicoMQTT.h>

const int LED_PIN = 2; 

// ==========================================
// 1. CONFIGURACIÓN DE TU RED WI-FI CASERA
// ==========================================
// Reemplaza estos valores con los datos exactos de tu router
const char* wifi_ssid = "Red5";
const char* wifi_password = "hola1234";

// ==========================================
// 2. CLASE PERSONALIZADA PARA EL BROKER MQTT
// ==========================================
class MiBrokerMQTT : public PicoMQTT::Server {
  protected:
    PicoMQTT::ConnectReturnCode auth(const char * client_id, const char * username, const char * password) override {
      if (!username || !password) {
        Serial.println("[AUTENTICACIÓN] Conexión rechazada: Faltan credenciales.");
        return PicoMQTT::CRC_NOT_AUTHORIZED;
      }

      if (strcmp(username, "Proyecto1") == 0 && strcmp(password, "IoThab1t4cion*") == 0) {
        Serial.printf("[AUTENTICACIÓN] Acceso concedido al cliente ID: %s\n", client_id);
        return PicoMQTT::CRC_ACCEPTED;
      }

      Serial.printf("[AUTENTICACIÓN] Credenciales inválidas del cliente ID: %s. Rechazado.\n", client_id);
      return PicoMQTT::CRC_NOT_AUTHORIZED;
    }
};

// Instanciar el broker
MiBrokerMQTT mqtt_server;

// ==========================================
// 3. CONFIGURACIÓN INICIAL (SETUP)
// ==========================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); 

  Serial.println("\n--- INICIANDO ESP32 COMO BROKER MQTT (MODO CLIENTE) ---");

  // Conectar a la red Wi-Fi existente
  Serial.print("Conectando a la red Wi-Fi: ");
  Serial.println(wifi_ssid);
  WiFi.begin(wifi_ssid, wifi_password);

  // Esperar a que se establezca la conexión
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Conexión Wi-Fi exitosa
  Serial.println("\n¡Conectado a la red Wi-Fi con éxito!");
  Serial.print("Nueva IP del Broker MQTT: ");
  Serial.println(WiFi.localIP()); // Esta IP la usaremos en la App

  // -----------------------------------------------------------
  // LÓGICA DE SUSCRIPCIÓN (Recibir mensajes desde la App)
  // -----------------------------------------------------------
  mqtt_server.subscribe("casa/led", [](const char* topic, const char* payload) {
    Serial.printf("[MQTT] Mensaje recibido en el tópico [%s]: %s\n", topic, payload);

    if (strcmp(payload, "1") == 0) {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("-> Led ON");
    } 
    else if (strcmp(payload, "0") == 0) {
      digitalWrite(LED_PIN, LOW);
      Serial.println("-> Led OFF");
    }
  });

  // Iniciar el servidor MQTT en el puerto 1883
  mqtt_server.begin();
  Serial.println("Servidor Broker MQTT listo y escuchando en 'casa/led'...");
}

// ==========================================
// 4. BUCLE PRINCIPAL (LOOP)
// ==========================================
void loop() {
  mqtt_server.loop();
}

/**
 * @file g2_puerta.ino
 * @brief Dispositivo ESP32 WROOM para control de seguridad (Puerta)
 * Sensores: KY-003 (Efecto Hall magnético) y KY-032 (Infrarrojo obstáculo)
 */

#include <WiFi.h>
#include <PubSubClient.h>

// ==========================================
// 1. CONFIGURACIÓN DE RED Y MQTT
// ==========================================
const char* ssid = "Red5";       // SSID del ESP32 que actúa como Broker
const char* password = "hola1234";   // Contraseña requerida
const char* mqtt_server = "192.168.2.59";   // IP por defecto del Access Point del Broker
const int mqtt_port = 1883;
const char* mqtt_user = "Proyecto1";
const char* mqtt_pass = "IoThab1t4cion*";

WiFiClient espClient;
PubSubClient client(espClient);

// ==========================================
// 2. DEFINICIÓN DE PINES Y VARIABLES
// ==========================================
#define HALL_PIN 18       // Pin digital conectado al KY-003 (Efecto Hall)
#define IR_PIN 19         // Pin digital conectado al KY-032 (Infrarrojo obstáculos)

unsigned long lastMsg = 0;
const long interval = 2000; // Intervalo de verificación en milisegundos (2 segundos)

// Variables para control de cambios de estado
int estadoHallAnt = -1;
int estadoIrAnt = -1;

// ==========================================
// 3. CONFIGURACIÓN DE CONEXIÓN WI-FI Y MQTT
// ==========================================
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a la red Wi-Fi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("¡Conectado a Wi-Fi exitosamente!");
  Serial.print("Dirección IP asignada: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    if (client.connect("ESP32Client_Puerta", mqtt_user, mqtt_pass)) {
      Serial.println("¡Conectado al Broker MQTT!");
    } else {
      Serial.print("Fallo, rc=");
      Serial.print(client.state());
      Serial.println(" Reintentando en 5 segundos...");
      delay(5000);
    }
  }
}

// ==========================================
// 4. CONFIGURACIÓN INICIAL (SETUP)
// ==========================================
void setup() {
  Serial.begin(115200);

  // Configurar pines de sensores como entrada
  pinMode(HALL_PIN, INPUT_PULLUP);
  pinMode(IR_PIN, INPUT);

  // Configurar red y servidor MQTT
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

// ==========================================
// 5. BUCLE PRINCIPAL (LOOP)
// ==========================================
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;

    // Lectura de los sensores digitales
    int estadoHall = digitalRead(HALL_PIN); // LOW suele indicar imán cerca (puerta cerrada)
    int estadoIr = digitalRead(IR_PIN);     // Depende del ajuste del potenciómetro del KY-032 (LOW = detección de objeto próximo)

    // Lógica combinada para determinar el estado preciso de la puerta
    // Hall = Cerrada (contacto magnético activo), IR = Presencia cercana u obstáculo intermedio
    String estadoPuerta = "";

    if (estadoHall == LOW) {
      estadoPuerta = "Cerrada";
    } else if (estadoHall == HIGH && estadoIr == LOW) {
      estadoPuerta = "Entrecerrada";
    } else {
      estadoPuerta = "Abierta";
    }

    // Mostrar información por la consola serial
    Serial.println("----------------------------------------");
    Serial.print("Sensor Hall (KY-003): "); Serial.println(estadoHall);
    Serial.print("Sensor IR   (KY-032): "); Serial.println(estadoIr);
    Serial.print("Estado de la Puerta:  "); Serial.println(estadoPuerta);

    // Publicar estado actual vía MQTT
    client.publish("habitacion/puerta/estado", estadoPuerta.c_str());
  }
}
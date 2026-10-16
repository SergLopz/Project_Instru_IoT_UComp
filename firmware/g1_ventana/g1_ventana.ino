/**
 * @file g1_ventana.ino
 * @brief Dispositivo ESP32 WROOM para monitoreo ambiental (Ventana)
 * Sensores: KY-015 (DHT11 - Temperatura/Humedad) y KY-018 (LDR - Luz ambiente)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

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
#define DHTPIN 4          // Pin digital conectado al KY-015 (DHT11)
#define DHTTYPE DHT11     // Definir tipo de sensor DHT
#define LDR_PIN 34        // Pin analógico conectado al KY-018 (LDR)

DHT dht(DHTPIN, DHTTYPE);
unsigned long lastMsg = 0;
const long interval = 5000; // Intervalo de envío en milisegundos (5 segundos)

// ==========================================
// 3. CONFIGURACIÓN DE CONEXIÓN WI-FI Y MQTT
// ==========================================
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("(g1_ventana) Conectando a la red Wi-Fi: ");
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
  // Bucle hasta conseguir conexión MQTT
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    // Intentar conectar con usuario y contraseña
    if (client.connect("ESP32Client_Ventana", mqtt_user, mqtt_pass)) {
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
  
  // Inicializar sensores
  dht.begin();
  pinMode(LDR_PIN, INPUT);

  // Configurar red y servidor MQTT
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

// ==========================================
// 5. BUCLE PRINCIPAL (LOOP)
// ==========================================
void loop() {
  // Asegurar la conexión MQTT activa
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  // Enviar datos cada vez que se cumpla el intervalo definido
  if (now - lastMsg > interval) {
    lastMsg = now;

    // Lectura de Temperatura y Humedad (KY-015)
    float humedad = dht.readHumidity();
    float temperatura = dht.readTemperature();

    // Lectura de Luminosidad (KY-018)
    int valorLDR = analogRead(LDR_PIN);
    
    // Determinar condición climática básica según valor analógico (ajustable según calibración)
    String estadoLuz = "";
    if (valorLDR > 3000) {
      estadoLuz = "Soleado";
    } else if (valorLDR > 1000) {
      estadoLuz = "Nublado";
    } else {
      estadoLuz = "Noche";
    }

    // Validar lecturas correctas del sensor DHT
    if (isnan(humedad) || isnan(temperatura)) {
      Serial.println("¡Error al leer el sensor KY-015 (DHT11)!");
      return;
    }

    // Mostrar información por la consola serial
    Serial.println("----------------------------------------");
    Serial.print("Temperatura: "); Serial.print(temperatura); Serial.println(" °C");
    Serial.print("Humedad:     "); Serial.print(humedad); Serial.println(" %");
    Serial.print("Luz LDR:     "); Serial.print(valorLDR); Serial.print(" -> "); Serial.println(estadoLuz);

    // Publicar los valores vía MQTT hacia los tópicos correspondientes
    client.publish("habitacion/ventana/temperatura", String(temperatura).c_str());
    client.publish("habitacion/ventana/humedad", String(humedad).c_str());
    client.publish("habitacion/ventana/luz_estado", estadoLuz.c_str());
  }
}
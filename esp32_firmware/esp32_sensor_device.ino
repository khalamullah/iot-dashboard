/*
 * ESP32 IoT Sensor Device
 * 
 * This firmware turns your ESP32 into a smart IoT sensor device that:
 * - Connects to WiFi
 * - Publishes sensor data via MQTT
 * - Receives control commands
 * - Auto-registers with the dashboard
 * 
 * Hardware Requirements:
 * - ESP32 Development Board
 * - DHT22 Temperature/Humidity Sensor (optional)
 * - LED (built-in or external)
 * - Relay module (optional for fan/appliance control)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// Include configuration
#include "config.h"

// DHT Sensor Setup
DHT dht(DHT_PIN, DHT_TYPE);

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Device state
bool ledState = false;
int fanSpeed = 0;
unsigned long lastSensorRead = 0;
unsigned long lastHeartbeat = 0;
unsigned long lastReconnectAttempt = 0;

// Function prototypes
void setupWiFi();
void reconnectMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void publishSensorData();
void publishHeartbeat();
void registerDevice();
void controlLED(bool state);
void controlFan(int speed);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=================================");
  Serial.println("ESP32 IoT Sensor Device");
  Serial.println("=================================");
  
  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  digitalWrite(FAN_PIN, LOW);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Connect to WiFi
  setupWiFi();
  
  // Setup MQTT
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  
  Serial.println("Setup complete!");
}

void loop() {
  // Maintain MQTT connection
  if (!mqttClient.connected()) {
    unsigned long now = millis();
    if (now - lastReconnectAttempt > 5000) {
      lastReconnectAttempt = now;
      reconnectMQTT();
    }
  } else {
    mqttClient.loop();
  }
  
  unsigned long now = millis();
  
  // Publish sensor data every SENSOR_INTERVAL
  if (now - lastSensorRead >= SENSOR_INTERVAL) {
    lastSensorRead = now;
    publishSensorData();
  }
  
  // Publish heartbeat every HEARTBEAT_INTERVAL
  if (now - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    lastHeartbeat = now;
    publishHeartbeat();
  }
}

void setupWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ WiFi Connection Failed!");
  }
}

void reconnectMQTT() {
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
    return;
  }
  
  Serial.print("Connecting to MQTT broker...");
  
  if (mqttClient.connect(DEVICE_ID, MQTT_USER, MQTT_PASSWORD)) {
    Serial.println(" ✓ Connected!");
    
    // Subscribe to control topic
    String controlTopic = String("iot/dashboard/") + DEVICE_ID + "/control";
    mqttClient.subscribe(controlTopic.c_str());
    Serial.print("✓ Subscribed to: ");
    Serial.println(controlTopic);
    
    // Register device with dashboard
    registerDevice();
    
  } else {
    Serial.print(" ✗ Failed, rc=");
    Serial.println(mqttClient.state());
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  
  // Parse JSON payload
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Extract command
  const char* command = doc["command"];
  
  if (strcmp(command, "LED") == 0) {
    const char* value = doc["value"];
    bool state = (strcmp(value, "ON") == 0);
    controlLED(state);
    Serial.print("💡 LED turned ");
    Serial.println(state ? "ON" : "OFF");
  }
  else if (strcmp(command, "FAN_SPEED") == 0) {
    int speed = doc["value"];
    controlFan(speed);
    Serial.print("🌀 Fan speed set to ");
    Serial.print(speed);
    Serial.println("%");
  }
}

void publishSensorData() {
  // Read sensor data
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Check if readings are valid
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("⚠ Failed to read from DHT sensor!");
    // Use simulated data for testing
    temperature = 25.0 + random(-50, 50) / 10.0;
    humidity = 50.0 + random(-100, 100) / 10.0;
  }
  
  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["device_id"] = DEVICE_ID;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["timestamp"] = millis();
  
  // Serialize to string
  char buffer[256];
  serializeJson(doc, buffer);
  
  // Publish to MQTT
  String sensorTopic = String("iot/dashboard/") + DEVICE_ID + "/sensors";
  mqttClient.publish(sensorTopic.c_str(), buffer);
  
  Serial.print("📊 Published: Temp=");
  Serial.print(temperature);
  Serial.print("°C, Humidity=");
  Serial.print(humidity);
  Serial.println("%");
}

void publishHeartbeat() {
  StaticJsonDocument<128> doc;
  doc["device_id"] = DEVICE_ID;
  doc["status"] = "online";
  doc["timestamp"] = millis();
  
  char buffer[128];
  serializeJson(doc, buffer);
  
  String statusTopic = String("iot/dashboard/") + DEVICE_ID + "/status";
  mqttClient.publish(statusTopic.c_str(), buffer);
}

void registerDevice() {
  StaticJsonDocument<512> doc;
  doc["device_id"] = DEVICE_ID;
  doc["device_name"] = DEVICE_NAME;
  doc["device_type"] = DEVICE_TYPE;
  doc["location"] = DEVICE_LOCATION;
  
  JsonObject capabilities = doc.createNestedObject("capabilities");
  capabilities["temperature"] = true;
  capabilities["humidity"] = true;
  capabilities["led_control"] = true;
  capabilities["fan_control"] = true;
  
  char buffer[512];
  serializeJson(doc, buffer);
  
  mqttClient.publish("iot/dashboard/register", buffer);
  
  Serial.println("✓ Device registration sent");
}

void controlLED(bool state) {
  ledState = state;
  digitalWrite(LED_PIN, state ? HIGH : LOW);
}

void controlFan(int speed) {
  fanSpeed = constrain(speed, 0, 100);
  
  // Convert percentage to PWM value (0-255)
  int pwmValue = map(fanSpeed, 0, 100, 0, 255);
  analogWrite(FAN_PIN, pwmValue);
}

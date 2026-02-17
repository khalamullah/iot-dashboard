/*
 * Configuration File for ESP32 IoT Device
 * 
 * IMPORTANT: Update these settings before uploading to your ESP32!
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============================================================================
// WiFi Configuration
// ============================================================================
#define WIFI_SSID "YOUR_WIFI_SSID"          // Replace with your WiFi network name
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"  // Replace with your WiFi password

// ============================================================================
// MQTT Configuration
// ============================================================================
#define MQTT_BROKER "broker.hivemq.com"     // Public MQTT broker (or use your own)
#define MQTT_PORT 1883
#define MQTT_USER ""                        // Leave empty for public brokers
#define MQTT_PASSWORD ""                    // Leave empty for public brokers

// ============================================================================
// Device Configuration
// ============================================================================
// Generate a unique ID for each device (e.g., "esp32_001", "esp32_kitchen", etc.)
#define DEVICE_ID "esp32_001"
#define DEVICE_NAME "ESP32 Sensor #1"
#define DEVICE_TYPE "ESP32"
#define DEVICE_LOCATION "Living Room"       // Physical location of the device

// ============================================================================
// Pin Configuration
// ============================================================================
#define DHT_PIN 4                           // GPIO pin for DHT22 sensor
#define DHT_TYPE DHT22                      // DHT sensor type (DHT11 or DHT22)
#define LED_PIN 2                           // GPIO pin for LED (built-in LED on most ESP32)
#define FAN_PIN 5                           // GPIO pin for fan/relay control

// ============================================================================
// Timing Configuration
// ============================================================================
#define SENSOR_INTERVAL 2000                // Send sensor data every 2 seconds (milliseconds)
#define HEARTBEAT_INTERVAL 30000            // Send heartbeat every 30 seconds (milliseconds)

#endif // CONFIG_H

# ESP32 Firmware Setup Guide

This guide will help you flash the IoT sensor firmware to your ESP32 device.

## 📋 Hardware Requirements

### Required Components

- **ESP32 Development Board** (any variant)
- **USB Cable** (for programming)
- **DHT22 Temperature/Humidity Sensor** (optional, firmware works without it)

### Optional Components

- **LED** (or use built-in LED)
- **Relay Module** (for controlling fans/appliances)
- **Breadboard and Jumper Wires**

## 🔌 Wiring Diagram

### DHT22 Sensor Connection

```
DHT22 Pin 1 (VCC)  → ESP32 3.3V
DHT22 Pin 2 (DATA) → ESP32 GPIO 4
DHT22 Pin 3 (NC)   → Not connected
DHT22 Pin 4 (GND)  → ESP32 GND
```

### LED Connection (if using external LED)

```
LED Anode (+)  → ESP32 GPIO 2 → 220Ω Resistor → LED Cathode (-) → GND
```

### Relay/Fan Connection

```
Relay VCC  → ESP32 5V (or 3.3V depending on relay)
Relay GND  → ESP32 GND
Relay IN   → ESP32 GPIO 5
```

## 🛠️ Software Setup

### Step 1: Install Arduino IDE

1. Download Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software)
2. Install and launch Arduino IDE

### Step 2: Add ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Click **OK**
5. Go to **Tools → Board → Boards Manager**
6. Search for "esp32"
7. Install "**esp32 by Espressif Systems**"

### Step 3: Install Required Libraries

Go to **Sketch → Include Library → Manage Libraries** and install:

1. **PubSubClient** by Nick O'Leary (for MQTT)
2. **ArduinoJson** by Benoit Blanchon (version 6.x)
3. **DHT sensor library** by Adafruit
4. **Adafruit Unified Sensor** (dependency for DHT)

### Step 4: Configure the Firmware

1. Open `config.h` in Arduino IDE
2. Update the following settings:

```cpp
// WiFi credentials
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"

// Device identification (make unique for each device)
#define DEVICE_ID "esp32_001"
#define DEVICE_NAME "ESP32 Sensor #1"
#define DEVICE_LOCATION "Living Room"
```

### Step 5: Upload to ESP32

1. Connect your ESP32 to your computer via USB
2. In Arduino IDE, select:
   - **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
   - **Tools → Port → [Select your ESP32's COM port]**
   - **Tools → Upload Speed → 115200**
3. Click the **Upload** button (→)
4. Wait for compilation and upload to complete

### Step 6: Monitor Serial Output

1. Open **Tools → Serial Monitor**
2. Set baud rate to **115200**
3. You should see output like:
   ```
   =================================
   ESP32 IoT Sensor Device
   =================================
   Connecting to WiFi: YourWiFiName
   ✓ WiFi Connected!
   IP Address: 192.168.1.xxx
   Connecting to MQTT broker... ✓ Connected!
   ✓ Device registration sent
   📊 Published: Temp=25.3°C, Humidity=52.1%
   ```

## 🎯 Testing Your Device

### 1. Verify WiFi Connection

- Check Serial Monitor for "✓ WiFi Connected!"
- Note the IP address assigned

### 2. Verify MQTT Connection

- Look for "✓ Connected!" message
- Device should auto-register with the dashboard

### 3. Check Dashboard

- Open your IoT dashboard at `http://localhost:8050`
- Your device should appear in the device list
- Sensor data should start appearing in real-time

### 4. Test Controls

- Try toggling the LED from the dashboard
- Adjust fan speed slider
- Verify commands are received (check Serial Monitor)

## 🔧 Troubleshooting

### WiFi Won't Connect

- Double-check SSID and password in `config.h`
- Ensure ESP32 is within WiFi range
- Try 2.4GHz network (ESP32 doesn't support 5GHz)

### MQTT Connection Fails

- Verify MQTT broker address
- Check if broker is accessible from your network
- Try using a different public broker (e.g., `test.mosquitto.org`)

### Sensor Reads NaN (Not a Number)

- Check DHT22 wiring
- Ensure DHT22 has proper power (3.3V)
- Add a 10kΩ pull-up resistor between DATA and VCC if needed
- Firmware will use simulated data if sensor fails

### Device Not Appearing in Dashboard

- Ensure dashboard is running
- Check that MQTT broker address matches in both firmware and dashboard
- Verify device is publishing to correct topics (check Serial Monitor)

## 📝 Pin Customization

If you need to use different GPIO pins, edit `config.h`:

```cpp
#define DHT_PIN 4      // Change to your preferred GPIO
#define LED_PIN 2      // Built-in LED or external
#define FAN_PIN 5      // Relay control pin
```

## 🔄 Adding Multiple Devices

To add more ESP32 devices:

1. Flash the same firmware to each device
2. **IMPORTANT:** Change `DEVICE_ID` in `config.h` for each device

   ```cpp
   // Device 1
   #define DEVICE_ID "esp32_kitchen"

   // Device 2
   #define DEVICE_ID "esp32_bedroom"
   ```

3. Each device will auto-register separately in the dashboard

## 📚 MQTT Topics Used

The firmware uses the following MQTT topic structure:

- **Sensor Data:** `iot/dashboard/{DEVICE_ID}/sensors`
- **Control Commands:** `iot/dashboard/{DEVICE_ID}/control`
- **Status/Heartbeat:** `iot/dashboard/{DEVICE_ID}/status`
- **Registration:** `iot/dashboard/register`

## 🎓 Next Steps

1. ✅ Flash firmware to ESP32
2. ✅ Verify device appears in dashboard
3. ✅ Test sensor readings and controls
4. 🔄 Add more devices by repeating the process
5. 🎨 Customize device names and locations
6. 📊 Monitor your IoT network!

## 💡 Tips

- Use descriptive device IDs (e.g., "esp32_kitchen", "esp32_garage")
- Keep firmware updated across all devices
- Monitor Serial output for debugging
- Consider using static IP for production deployments
- Add battery backup for critical sensors

---

**Need Help?** Check the Serial Monitor output for detailed error messages and connection status.

# Device Setup Guide

Complete guide for adding and managing IoT devices in your dashboard.

## 🎯 Quick Start

### Option 1: ESP32 Devices (Recommended)

1. Flash the provided firmware to your ESP32
2. Device auto-registers with the dashboard
3. Start monitoring immediately

See [ESP32 Firmware Setup](esp32_firmware/README.md) for detailed instructions.

### Option 2: Manual Device Registration

1. Open dashboard at `http://localhost:8050`
2. Click "Add Device" button
3. Fill in device details
4. Configure your device to publish to the correct MQTT topics

## 📡 MQTT Topic Structure

All devices communicate using device-specific MQTT topics:

### Topics Your Device Should Publish To:

**Sensor Data:**

```
Topic: iot/dashboard/{DEVICE_ID}/sensors
Payload: {
    "device_id": "your_device_id",
    "temperature": 25.5,
    "humidity": 60.2,
    "timestamp": "2024-01-01T12:00:00"
}
```

**Status/Heartbeat (every 30 seconds):**

```
Topic: iot/dashboard/{DEVICE_ID}/status
Payload: {
    "device_id": "your_device_id",
    "status": "online",
    "timestamp": 1234567890
}
```

**Device Registration (on startup):**

```
Topic: iot/dashboard/register
Payload: {
    "device_id": "your_device_id",
    "device_name": "Living Room Sensor",
    "device_type": "ESP32",
    "location": "Living Room",
    "capabilities": {
        "temperature": true,
        "humidity": true,
        "led_control": true,
        "fan_control": true
    }
}
```

### Topics Your Device Should Subscribe To:

**Control Commands:**

```
Topic: iot/dashboard/{DEVICE_ID}/control
Payload: {
    "command": "LED",
    "value": "ON",
    "timestamp": "2024-01-01T12:00:00"
}
```

**Supported Commands:**

- `LED` with value `"ON"` or `"OFF"`
- `FAN_SPEED` with value `0-100` (percentage)

## 🔧 Supported Device Types

### ESP32

- **Best for:** WiFi-enabled sensors with control capabilities
- **Setup:** Flash provided firmware
- **Features:** Auto-registration, temperature, humidity, LED, fan control

### Arduino (with WiFi/Ethernet Shield)

- **Best for:** Simple sensor nodes
- **Setup:** Adapt ESP32 firmware or use MQTT library
- **Features:** Sensor data publishing

### Raspberry Pi

- **Best for:** Complex processing, multiple sensors
- **Setup:** Use Python MQTT client
- **Features:** Full control and monitoring

### Custom Devices

- **Best for:** Any device with MQTT capability
- **Setup:** Implement MQTT client following topic structure
- **Features:** Flexible integration

## 🐍 Python Example (Raspberry Pi / Generic)

```python
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
DEVICE_ID = "rpi_001"

client = mqtt.Client(client_id=DEVICE_ID)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to control topic
    client.subscribe(f"iot/dashboard/{DEVICE_ID}/control")

    # Register device
    registration = {
        "device_id": DEVICE_ID,
        "device_name": "Raspberry Pi Sensor",
        "device_type": "RaspberryPi",
        "location": "Office",
        "capabilities": {
            "temperature": True,
            "humidity": True
        }
    }
    client.publish("iot/dashboard/register", json.dumps(registration))

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    command = payload.get('command')
    value = payload.get('value')
    print(f"Received command: {command} = {value}")
    # Handle commands here

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# Main loop - publish sensor data
while True:
    sensor_data = {
        "device_id": DEVICE_ID,
        "temperature": 25.0,  # Read from actual sensor
        "humidity": 50.0,     # Read from actual sensor
        "timestamp": datetime.now().isoformat()
    }

    client.publish(f"iot/dashboard/{DEVICE_ID}/sensors", json.dumps(sensor_data))

    # Heartbeat
    heartbeat = {
        "device_id": DEVICE_ID,
        "status": "online",
        "timestamp": time.time()
    }
    client.publish(f"iot/dashboard/{DEVICE_ID}/status", json.dumps(heartbeat))

    time.sleep(2)
```

## 🔍 Troubleshooting

### Device Not Appearing in Dashboard

**Check:**

1. MQTT broker address matches in both device and dashboard
2. Device is publishing to correct topics
3. Registration message was sent
4. Dashboard is running and connected to MQTT

**Solution:**

- Check device serial output for connection status
- Verify MQTT broker is accessible
- Try manual device registration via dashboard UI

### Device Shows as Offline

**Possible Causes:**

- Device stopped sending heartbeat messages
- Network connectivity issues
- Device crashed or restarted

**Solution:**

- Check device power and network
- Verify heartbeat messages are being sent every 30 seconds
- Restart device
- Check dashboard logs for MQTT messages

### Sensor Data Not Updating

**Check:**

1. Device is publishing to `iot/dashboard/{DEVICE_ID}/sensors`
2. Payload format matches expected JSON structure
3. Device is marked as "online" in dashboard

**Solution:**

- Verify topic name includes correct device ID
- Check JSON payload structure
- Monitor MQTT broker for published messages

### Control Commands Not Working

**Check:**

1. Device is subscribed to `iot/dashboard/{DEVICE_ID}/control`
2. Device is handling incoming messages
3. MQTT connection is stable

**Solution:**

- Verify subscription topic in device code
- Add debug logging for received messages
- Test with MQTT client tool (e.g., MQTT Explorer)

## 📊 Dashboard Features

### Device List

- View all registered devices
- See online/offline status
- Click device to view details

### Real-Time Monitoring

- Live temperature and humidity graphs
- Current readings display
- Data point counter
- Last update timestamp

### Device Control

- LED on/off control
- Fan speed adjustment (0-100%)
- Instant command feedback

### Device Management

- Add devices manually
- Auto-registration from ESP32
- Device status tracking
- Heartbeat monitoring

## 🔐 Security Considerations

### For Production Use:

1. **Use Private MQTT Broker**
   - Don't use public brokers for sensitive data
   - Set up Mosquitto or similar on your network

2. **Enable Authentication**
   - Configure MQTT username/password
   - Update device firmware with credentials

3. **Use TLS/SSL**
   - Enable encrypted MQTT connections
   - Use port 8883 instead of 1883

4. **Network Isolation**
   - Keep IoT devices on separate VLAN
   - Use firewall rules to restrict access

## 📈 Scaling

### Adding Many Devices:

- Each device auto-registers
- Dashboard handles multiple devices efficiently
- Database stores all historical data
- Select device to view individual data

### Performance Tips:

- Adjust sensor publish interval (default: 2 seconds)
- Increase heartbeat interval for stable devices
- Clean old data from database periodically
- Use database indexes for faster queries

## 🎓 Next Steps

1. ✅ Set up your first device (ESP32 recommended)
2. ✅ Verify device appears in dashboard
3. ✅ Test sensor readings and controls
4. 🔄 Add more devices
5. 📊 Monitor your IoT network
6. 🎨 Customize for your needs

---

**Need Help?** Check the ESP32 firmware README or dashboard logs for detailed error messages.

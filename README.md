# IoT Cloud Dashboard - Multi-Device Support

A production-ready IoT dashboard with comprehensive device management, MQTT integration, real-time visualization, and support for multiple devices including ESP32, Arduino, and Raspberry Pi.

## ✨ Features

### Device Management

- 🔌 **Auto-Registration**: ESP32 devices automatically register on first connection
- 📝 **Manual Registration**: Add devices via dashboard UI
- 📊 **Multi-Device Support**: Monitor unlimited devices simultaneously
- 🟢 **Status Tracking**: Real-time online/offline status with heartbeat monitoring
- 🎛️ **Per-Device Controls**: Individual LED and fan control for each device

### Data Visualization

- 📈 **Real-Time Graphs**: Live temperature and humidity charts
- 📉 **Historical Data**: View past 24 hours of sensor readings
- 🎨 **Modern UI**: Dark theme with glassmorphism effects
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile

### Communication

- 📡 **MQTT Protocol**: Industry-standard IoT messaging
- 🔄 **Bi-Directional**: Send commands and receive data
- 🌐 **Cloud-Ready**: Works with public or private MQTT brokers
- 🔐 **Secure**: Support for TLS/SSL and authentication

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

**Option A: Multi-Device Dashboard (Recommended)**

```bash
python dashboard_multidevice.py
```

**Option B: Original Single-Device Dashboard**

```bash
python dashboard.py
```

### 3. Open in Browser

Navigate to: `http://localhost:8050`

### 4. Add Your First Device

**Option A: ESP32 (Automated)**

1. Flash the ESP32 firmware (see `esp32_firmware/README.md`)
2. Device auto-registers and appears in dashboard
3. Start monitoring immediately!

**Option B: Manual Registration**

1. Click "Add Device" in the dashboard
2. Enter device details
3. Configure your device to publish to MQTT topics (see `DEVICE_SETUP.md`)

## 📁 Project Structure

```
IOT DASHBOARD/
├── dashboard.py                    # Original single-device dashboard
├── dashboard_multidevice.py        # Enhanced multi-device dashboard ⭐
├── device_manager.py               # Device registration and management
├── mock_device.py                  # Simulated device for testing
├── requirements.txt                # Python dependencies
├── iot_data.db                     # SQLite database (auto-created)
├── DEVICE_SETUP.md                 # Complete device setup guide
├── README.md                       # This file
└── esp32_firmware/                 # ESP32 firmware files
    ├── esp32_sensor_device.ino     # Main Arduino sketch
    ├── config.h                    # Configuration file
    └── README.md                   # ESP32 setup instructions
```

## 🔧 Supported Devices

### ESP32 ⭐ Recommended

- **Firmware Included**: Ready-to-flash Arduino sketch
- **Auto-Registration**: Connects and registers automatically
- **Full Features**: Temperature, humidity, LED, fan control
- **Setup Time**: ~15 minutes

### Arduino

- **WiFi/Ethernet Required**: Use WiFi or Ethernet shield
- **MQTT Library**: Use PubSubClient library
- **Adaptation Needed**: Modify ESP32 firmware for your board

### Raspberry Pi

- **Python MQTT**: Use paho-mqtt library
- **Full Control**: Complete flexibility
- **Example Included**: See `DEVICE_SETUP.md`

### Custom Devices

- **Any MQTT Client**: Works with any device supporting MQTT
- **Topic Structure**: Follow documented MQTT topics
- **Flexible Integration**: Adapt to your needs

## 📡 MQTT Topics

### Device → Dashboard (Publish)

```
iot/dashboard/{device_id}/sensors    # Sensor data
iot/dashboard/{device_id}/status     # Heartbeat/status
iot/dashboard/register               # Device registration
```

### Dashboard → Device (Subscribe)

```
iot/dashboard/{device_id}/control    # Control commands
```

See `DEVICE_SETUP.md` for detailed payload formats.

## 🎮 Testing with Mock Device

Test the system without physical hardware:

```bash
# Terminal 1: Run dashboard
python dashboard_multidevice.py

# Terminal 2: Run mock device
python mock_device.py
```

The mock device simulates an ESP32 with temperature/humidity sensors.

## 📊 Database Schema

### `devices` Table

Stores registered device information:

- device_id (PRIMARY KEY)
- device_name
- device_type
- location
- capabilities (JSON)
- registered_at
- last_seen
- status

### `sensor_data` Table

Historical sensor readings:

- id (PRIMARY KEY)
- timestamp
- temperature
- humidity
- device_id

### `control_commands` Table

Command history:

- id (PRIMARY KEY)
- timestamp
- command_type
- command_value
- device_id

## 🎯 Use Cases

### Home Automation

- Monitor temperature and humidity in multiple rooms
- Control lights and fans remotely
- Track environmental conditions over time

### Industrial Monitoring

- Monitor equipment temperature
- Track environmental conditions in facilities
- Alert on abnormal readings

### Agriculture

- Monitor greenhouse conditions
- Control irrigation systems
- Track soil moisture and temperature

### Research & Education

- Learn IoT development
- Prototype sensor networks
- Experiment with MQTT

## 🔐 Security Best Practices

### For Production Deployment:

1. **Use Private MQTT Broker**
   - Install Mosquitto on your server
   - Don't use public brokers for sensitive data

2. **Enable Authentication**

   ```python
   MQTT_USER = "your_username"
   MQTT_PASSWORD = "your_password"
   ```

3. **Use TLS/SSL**
   - Enable encrypted connections
   - Use port 8883 instead of 1883

4. **Network Isolation**
   - Separate VLAN for IoT devices
   - Firewall rules to restrict access

5. **Change Default Credentials**
   - Update ESP32 WiFi credentials
   - Use strong passwords

## 🛠️ Customization

### Add New Sensor Types

1. Update device capabilities in registration
2. Modify MQTT payload structure
3. Add visualization in dashboard

### Change Update Intervals

```python
# In ESP32 firmware (config.h)
#define SENSOR_INTERVAL 2000      # Milliseconds
#define HEARTBEAT_INTERVAL 30000  # Milliseconds
```

### Custom MQTT Broker

```python
# In dashboard_multidevice.py
MQTT_BROKER = "your-broker.com"
MQTT_PORT = 1883
```

## 📚 Documentation

- **[DEVICE_SETUP.md](DEVICE_SETUP.md)**: Complete device setup guide
- **[esp32_firmware/README.md](esp32_firmware/README.md)**: ESP32 firmware setup
- **Code Comments**: Inline documentation in all files

## 🐛 Troubleshooting

### Dashboard won't start

- Check if port 8050 is available
- Verify all dependencies are installed
- Check Python version (3.7+)

### Device not appearing

- Verify MQTT broker connection
- Check device is publishing to correct topics
- Ensure device sent registration message

### Sensor data not updating

- Check device online status
- Verify MQTT topic structure
- Monitor MQTT broker for messages

### Control commands not working

- Ensure device subscribed to control topic
- Check MQTT connection stability
- Verify payload format

See `DEVICE_SETUP.md` for detailed troubleshooting.

## 📦 Dependencies

```
dash>=2.14.0
dash-bootstrap-components>=1.5.0
plotly>=5.17.0
paho-mqtt>=1.6.1
```

For ESP32:

- PubSubClient
- ArduinoJson
- DHT sensor library
- Adafruit Unified Sensor

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional sensor types
- More control options
- Advanced analytics
- Mobile app
- Alert system
- Data export features

## 📄 License

This project is open source and available for educational and commercial use.

## 🎓 Learning Resources

- **MQTT Protocol**: [mqtt.org](https://mqtt.org)
- **ESP32 Development**: [espressif.com](https://www.espressif.com)
- **Dash Framework**: [dash.plotly.com](https://dash.plotly.com)
- **Plotly Graphs**: [plotly.com/python](https://plotly.com/python)

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Run dashboard
3. ✅ Test with mock device
4. 🔄 Flash ESP32 firmware
5. 🔄 Add physical devices
6. 🔄 Customize for your needs
7. 📊 Monitor your IoT network!

---

**Built with ❤️ for the IoT community**

For questions or issues, check the documentation files or review the code comments.

# ESP32 Firmware - PlatformIO Project

This directory contains the ESP32 firmware that can be uploaded using **PlatformIO** in VS Code.

## 🚀 Quick Start with PlatformIO

### Step 1: Install VS Code and PlatformIO

1. **Install Visual Studio Code:**
   - Download from: https://code.visualstudio.com/
   - Install and open VS Code

2. **Install PlatformIO Extension:**
   - Open VS Code
   - Click Extensions icon (or press `Ctrl+Shift+X`)
   - Search for: `PlatformIO IDE`
   - Click **Install**
   - Wait for installation to complete (may take a few minutes)
   - Reload VS Code if prompted

### Step 2: Open the Project

1. **Open PlatformIO Home:**
   - Click the PlatformIO icon (alien head) in the left sidebar
   - Click **"Open"** under PIO Home

2. **Open Project:**
   - Click **"Open Project"**
   - Navigate to: `C:\Users\Khalamullah\Desktop\IOT DASHBOARD\esp32_firmware`
   - Click **"Open"**

### Step 3: Configure Your Device

1. **Edit `config.h`:**
   - Open `config.h` in VS Code
   - Update WiFi credentials:
     ```cpp
     #define WIFI_SSID "YourWiFiName"
     #define WIFI_PASSWORD "YourWiFiPassword"
     ```
   - Set unique device ID:
     ```cpp
     #define DEVICE_ID "esp32_001"
     #define DEVICE_NAME "ESP32 Sensor #1"
     #define DEVICE_LOCATION "Living Room"
     ```
   - Save file (`Ctrl+S`)

### Step 4: Connect ESP32

1. **Plug in your ESP32** via USB cable
2. **Check COM Port:**
   - PlatformIO will auto-detect the port
   - Or manually set in `platformio.ini`:
     ```ini
     upload_port = COM3  ; Change to your port
     ```

### Step 5: Build and Upload

#### Option A: Using PlatformIO Toolbar

1. Look at the bottom toolbar in VS Code
2. Click the **→ (Upload)** button
3. PlatformIO will:
   - Download required libraries
   - Compile the code
   - Upload to ESP32

#### Option B: Using PlatformIO Menu

1. Click PlatformIO icon in sidebar
2. Expand **"PROJECT TASKS"**
3. Expand **"esp32dev"**
4. Click **"Upload"**

#### Option C: Using Command Palette

1. Press `Ctrl+Shift+P`
2. Type: `PlatformIO: Upload`
3. Press Enter

### Step 6: Monitor Serial Output

1. **Open Serial Monitor:**
   - Click the **🔌 (Serial Monitor)** button in bottom toolbar
   - Or: PlatformIO → PROJECT TASKS → esp32dev → Monitor

2. **You should see:**
   ```
   =================================
   ESP32 IoT Sensor Device
   =================================
   Connecting to WiFi: YourWiFiName
   ✓ WiFi Connected!
   IP Address: 192.168.1.XXX
   Connecting to MQTT broker... ✓ Connected!
   ✓ Device registration sent
   📊 Published: Temp=25.3°C, Humidity=52.1%
   ```

---

## 📁 Project Structure

```
esp32_firmware/
├── platformio.ini          # PlatformIO configuration
├── esp32_sensor_device.ino # Main firmware code
├── config.h                # Configuration file (edit this!)
└── PLATFORMIO_GUIDE.md     # This file
```

---

## 🎯 PlatformIO Commands

All commands available in VS Code bottom toolbar:

- **✓ Build** - Compile code without uploading
- **→ Upload** - Build and upload to ESP32
- **🔌 Serial Monitor** - View ESP32 output
- **🗑️ Clean** - Clean build files
- **🏠 PlatformIO Home** - Open PlatformIO home page

---

## 🔧 Advanced Configuration

### Change Upload Port

Edit `platformio.ini`:

```ini
upload_port = COM3  ; Windows
; upload_port = /dev/ttyUSB0  ; Linux
; upload_port = /dev/cu.usbserial-*  ; macOS
```

### Change Upload Speed

Edit `platformio.ini`:

```ini
upload_speed = 115200  ; Slower but more reliable
; upload_speed = 921600  ; Faster (default)
```

### Enable Debug Output

Already enabled in `platformio.ini`:

```ini
build_flags =
    -DCORE_DEBUG_LEVEL=3
```

---

## 🐛 Troubleshooting

### "No device found"

- Check USB cable connection
- Try different USB port
- Install CH340 or CP210x drivers
- Check Device Manager for COM port

### "Upload failed"

- Hold BOOT button while uploading
- Try lower upload speed (115200)
- Check correct COM port in platformio.ini

### "Library not found"

- PlatformIO auto-downloads libraries
- Check internet connection
- Try: PlatformIO → Clean
- Then rebuild

### "WiFi connection failed"

- Check WiFi credentials in config.h
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Move ESP32 closer to router

---

## ✅ Advantages of PlatformIO

- ✅ **Auto-installs libraries** - No manual library installation
- ✅ **Better code completion** - IntelliSense works better
- ✅ **Faster builds** - Incremental compilation
- ✅ **Multiple boards** - Easy to switch between ESP32 variants
- ✅ **Built-in serial monitor** - No need to switch windows
- ✅ **Professional workflow** - Used in production environments

---

## 📚 Next Steps

1. ✅ Install VS Code and PlatformIO
2. ✅ Open this project in PlatformIO
3. ✅ Edit config.h with your WiFi credentials
4. ✅ Connect ESP32 via USB
5. ✅ Click Upload button
6. ✅ Open Serial Monitor to verify
7. ✅ Check dashboard - device should appear!

---

## 🆚 PlatformIO vs Arduino IDE

| Feature             | PlatformIO | Arduino IDE |
| ------------------- | ---------- | ----------- |
| Library Management  | Automatic  | Manual      |
| Code Completion     | Excellent  | Basic       |
| Build Speed         | Fast       | Slower      |
| Multi-board Support | Easy       | Manual      |
| Professional Use    | Yes        | Hobbyist    |
| Learning Curve      | Moderate   | Easy        |

---

**You're all set! Upload your code with one click! 🚀**

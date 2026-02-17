# How to Upload ESP32 Code to Your Board

## 📋 What You'll Need

### Hardware

- ✅ ESP32 development board
- ✅ USB cable (usually micro-USB or USB-C depending on your board)
- ✅ Computer with USB port

### Software

- ✅ Arduino IDE (we'll install this together)

---

## 🔧 Step-by-Step Installation

### Step 1: Install Arduino IDE

1. **Download Arduino IDE:**
   - Go to: https://www.arduino.cc/en/software
   - Click **"Windows Win 10 and newer"** (or your OS)
   - Download the installer

2. **Install Arduino IDE:**
   - Run the downloaded installer
   - Follow the installation wizard
   - Accept default settings
   - Click "Install"

---

### Step 2: Add ESP32 Board Support

1. **Open Arduino IDE**

2. **Open Preferences:**
   - Click **File → Preferences**
   - Or press `Ctrl + Comma`

3. **Add ESP32 Board Manager URL:**
   - Find the box labeled **"Additional Board Manager URLs"**
   - Paste this URL:
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Click **OK**

4. **Install ESP32 Board:**
   - Click **Tools → Board → Boards Manager**
   - In the search box, type: `esp32`
   - Find **"esp32 by Espressif Systems"**
   - Click **Install** (this may take a few minutes)
   - Wait for installation to complete
   - Click **Close**

---

### Step 3: Install Required Libraries

1. **Open Library Manager:**
   - Click **Sketch → Include Library → Manage Libraries**
   - Or press `Ctrl + Shift + I`

2. **Install these libraries one by one:**

   **Library 1: PubSubClient**
   - Search: `PubSubClient`
   - Find: **"PubSubClient by Nick O'Leary"**
   - Click **Install**

   **Library 2: ArduinoJson**
   - Search: `ArduinoJson`
   - Find: **"ArduinoJson by Benoit Blanchon"**
   - Click **Install** (install version 6.x)

   **Library 3: DHT sensor library**
   - Search: `DHT sensor library`
   - Find: **"DHT sensor library by Adafruit"**
   - Click **Install**
   - If prompted to install dependencies, click **"Install all"**

   **Library 4: Adafruit Unified Sensor**
   - Search: `Adafruit Unified Sensor`
   - Find: **"Adafruit Unified Sensor"**
   - Click **Install**

3. **Close Library Manager**

---

### Step 4: Open the ESP32 Code

1. **Navigate to your code:**
   - In Arduino IDE, click **File → Open**
   - Browse to: `C:\Users\Khalamullah\Desktop\IOT DASHBOARD\esp32_firmware\`
   - Select: `esp32_sensor_device.ino`
   - Click **Open**

2. **You should see two tabs:**
   - `esp32_sensor_device` (main code)
   - `config.h` (configuration)

---

### Step 5: Configure Your Device

1. **Click on the `config.h` tab**

2. **Update WiFi Settings:**

   ```cpp
   #define WIFI_SSID "YOUR_WIFI_NAME"        // Replace with your WiFi name
   #define WIFI_PASSWORD "YOUR_WIFI_PASSWORD" // Replace with your WiFi password
   ```

3. **Update Device ID (make it unique):**

   ```cpp
   #define DEVICE_ID "esp32_001"              // Change to: esp32_kitchen, esp32_bedroom, etc.
   #define DEVICE_NAME "ESP32 Sensor #1"      // Change to a friendly name
   #define DEVICE_LOCATION "Living Room"      // Change to actual location
   ```

4. **Save the file:**
   - Press `Ctrl + S`

---

### Step 6: Connect Your ESP32

1. **Connect ESP32 to Computer:**
   - Plug USB cable into ESP32
   - Plug other end into your computer
   - ESP32 should power on (LED may light up)

2. **Install USB Driver (if needed):**
   - Windows usually installs drivers automatically
   - If not recognized, you may need CP210x or CH340 driver
   - Download from: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

---

### Step 7: Select Board and Port

1. **Select Board Type:**
   - Click **Tools → Board → ESP32 Arduino**
   - Select: **"ESP32 Dev Module"**
   - (If you have a specific board like ESP32-WROOM, select that instead)

2. **Select COM Port:**
   - Click **Tools → Port**
   - Select the COM port with your ESP32 (e.g., `COM3`, `COM4`)
   - It usually shows as: `COM# (USB-SERIAL CH340)` or similar
   - **If you don't see any ports:**
     - Unplug and replug the USB cable
     - Try a different USB cable
     - Check Device Manager for USB devices

3. **Set Upload Speed:**
   - Click **Tools → Upload Speed**
   - Select: **115200**

---

### Step 8: Upload Code to ESP32

1. **Verify Code (Optional but Recommended):**
   - Click the **✓ Verify** button (checkmark icon)
   - Wait for compilation
   - Should say: "Done compiling"

2. **Upload Code:**
   - Click the **→ Upload** button (right arrow icon)
   - You'll see:
     ```
     Sketch uses XXXX bytes...
     Connecting........___....
     Writing at 0x00001000...
     ```
   - **Wait for upload to complete** (30-60 seconds)
   - Should say: **"Hard resetting via RTS pin..."**

3. **If Upload Fails:**
   - **Hold the BOOT button** on ESP32 while clicking Upload
   - Release BOOT button when you see "Connecting..."
   - Some boards require this for first upload

---

### Step 9: Verify It's Working

1. **Open Serial Monitor:**
   - Click **Tools → Serial Monitor**
   - Or press `Ctrl + Shift + M`

2. **Set Baud Rate:**
   - At bottom right of Serial Monitor
   - Select: **115200 baud**

3. **Press RESET button on ESP32**

4. **You should see output like:**
   ```
   =================================
   ESP32 IoT Sensor Device
   =================================
   Connecting to WiFi: YourWiFiName
   .....
   ✓ WiFi Connected!
   IP Address: 192.168.1.XXX
   Connecting to MQTT broker... ✓ Connected!
   ✓ Subscribed to: iot/dashboard/esp32_001/control
   ✓ Device registration sent
   📊 Published: Temp=25.3°C, Humidity=52.1%
   ```

---

## ✅ Success Checklist

- [ ] Arduino IDE installed
- [ ] ESP32 board support installed
- [ ] All 4 libraries installed
- [ ] Code opened in Arduino IDE
- [ ] WiFi credentials configured
- [ ] Device ID set to unique value
- [ ] ESP32 connected via USB
- [ ] Correct board selected
- [ ] Correct COM port selected
- [ ] Code uploaded successfully
- [ ] Serial Monitor shows WiFi connected
- [ ] Serial Monitor shows MQTT connected
- [ ] Device appears in dashboard

---

## 🐛 Troubleshooting

### "Port not found" or "No COM port available"

**Solution:**

- Unplug and replug USB cable
- Try different USB port
- Install CH340 or CP210x USB driver
- Check Device Manager → Ports (COM & LPT)

### "Failed to connect to ESP32"

**Solution:**

- Hold BOOT button while uploading
- Try lower upload speed (115200)
- Press RESET button before upload
- Check USB cable (try different cable)

### "WiFi connection failed"

**Solution:**

- Double-check WiFi name and password
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Move ESP32 closer to router
- Check WiFi credentials have no special characters

### "MQTT connection failed"

**Solution:**

- Check internet connection
- Verify MQTT broker address
- Try different public broker: `test.mosquitto.org`
- Check firewall settings

### "Device not appearing in dashboard"

**Solution:**

- Ensure dashboard is running
- Check Serial Monitor for "Device registration sent"
- Verify MQTT broker matches in both dashboard and ESP32
- Refresh dashboard page

---

## 🎯 Next Steps

Once your ESP32 is working:

1. **Check Dashboard:**
   - Open: http://localhost:8050
   - Your device should appear in the device list
   - Click on it to see sensor data

2. **Test Controls:**
   - Try LED ON/OFF buttons
   - Adjust fan speed slider
   - Watch Serial Monitor for command reception

3. **Add More Devices:**
   - Flash same code to another ESP32
   - Change DEVICE_ID to unique value
   - Both devices will appear in dashboard

4. **Connect Real Sensors:**
   - Connect DHT22 sensor (see wiring in main README)
   - Connect LED to GPIO 2
   - Connect relay to GPIO 5

---

## 📞 Need Help?

- Check Serial Monitor output for error messages
- Review `esp32_firmware/README.md` for detailed wiring
- See `DEVICE_SETUP.md` for MQTT topic details
- Check Arduino IDE error messages carefully

---

**You're all set! Your ESP32 should now be sending data to your dashboard! 🎉**

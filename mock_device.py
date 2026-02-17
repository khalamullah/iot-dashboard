"""
Mock IoT Device Simulator - Multi-Device Support
Simulates multiple physical IoT devices sending sensor data via MQTT
Compatible with the new device management system
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# MQTT Configuration - Must match dashboard settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# Device Configuration
DEVICE_ID = "mock_device_001"
DEVICE_NAME = "Mock Sensor #1"
DEVICE_TYPE = "Mock"
DEVICE_LOCATION = "Test Lab"

MQTT_CLIENT_ID = DEVICE_ID + "_" + str(int(time.time()))

# Device state
device_state = {
    "led_status": "OFF",
    "fan_speed": 0
}

def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects."""
    if rc == 0:
        print("✓ Mock Device connected to MQTT Broker!")
        
        # Subscribe to device-specific control topic
        control_topic = f"iot/dashboard/{DEVICE_ID}/control"
        client.subscribe(control_topic)
        print(f"✓ Subscribed to control topic: {control_topic}")
        
        # Register device with dashboard
        register_device(client)
    else:
        print(f"✗ Connection failed, return code {rc}")

def on_message(client, userdata, msg):
    """Callback when control command is received."""
    try:
        payload = json.loads(msg.payload.decode())
        command = payload.get('command')
        value = payload.get('value')
        
        if command == "LED":
            device_state["led_status"] = value
            print(f"💡 LED turned {value}")
        elif command == "FAN_SPEED":
            device_state["fan_speed"] = value
            print(f"🌀 Fan speed set to {value}%")
        
        print(f"📥 Received command: {command} = {value}")
    except Exception as e:
        print(f"Error processing control message: {e}")

def register_device(client):
    """Register device with the dashboard."""
    registration_payload = {
        "device_id": DEVICE_ID,
        "device_name": DEVICE_NAME,
        "device_type": DEVICE_TYPE,
        "location": DEVICE_LOCATION,
        "capabilities": {
            "temperature": True,
            "humidity": True,
            "led_control": True,
            "fan_control": True
        }
    }
    
    client.publish("iot/dashboard/register", json.dumps(registration_payload))
    print(f"✓ Device registration sent: {DEVICE_NAME}")

def generate_sensor_data():
    """Generate realistic mock sensor data."""
    # Base temperature: 20-30°C with small random variations
    base_temp = 25
    temp_variation = random.gauss(0, 2)  # Gaussian noise
    temperature = round(base_temp + temp_variation, 2)
    
    # Base humidity: 40-60% with variations
    base_humidity = 50
    humidity_variation = random.gauss(0, 5)
    humidity = round(max(0, min(100, base_humidity + humidity_variation)), 2)
    
    # Fan affects temperature (higher fan speed = lower temp)
    if device_state["fan_speed"] > 0:
        temperature -= device_state["fan_speed"] * 0.05
    
    return {
        "device_id": DEVICE_ID,
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "timestamp": datetime.now().isoformat()
    }

def publish_heartbeat(client):
    """Publish device heartbeat/status."""
    heartbeat_payload = {
        "device_id": DEVICE_ID,
        "status": "online",
        "timestamp": int(time.time())
    }
    
    status_topic = f"iot/dashboard/{DEVICE_ID}/status"
    client.publish(status_topic, json.dumps(heartbeat_payload))

def main():
    """Main function to run the mock device."""
    print("\n" + "="*60)
    print("🔌 Mock IoT Device Starting...")
    print("="*60)
    print(f"📡 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"🆔 Device ID: {DEVICE_ID}")
    print(f"📛 Device Name: {DEVICE_NAME}")
    print(f"📤 Publishing to: iot/dashboard/{DEVICE_ID}/sensors")
    print(f"📥 Listening on: iot/dashboard/{DEVICE_ID}/control")
    print("="*60 + "\n")
    
    # Create MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect to broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"❌ Failed to connect to MQTT broker: {e}")
        return
    
    # Main loop - send sensor data every 2 seconds
    last_heartbeat = time.time()
    try:
        print("🚀 Device is running. Press Ctrl+C to stop.\n")
        while True:
            # Generate and publish sensor data
            sensor_data = generate_sensor_data()
            sensor_topic = f"iot/dashboard/{DEVICE_ID}/sensors"
            payload = json.dumps(sensor_data)
            client.publish(sensor_topic, payload)
            
            print(f"📊 Published: Temp={sensor_data['temperature']}°C, "
                  f"Humidity={sensor_data['humidity']}% | "
                  f"LED={device_state['led_status']}, "
                  f"Fan={device_state['fan_speed']}%")
            
            # Send heartbeat every 30 seconds
            current_time = time.time()
            if current_time - last_heartbeat >= 30:
                publish_heartbeat(client)
                last_heartbeat = current_time
            
            time.sleep(2)  # Send data every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping mock device...")
        client.loop_stop()
        client.disconnect()
        print("✓ Device stopped successfully")

if __name__ == "__main__":
    main()
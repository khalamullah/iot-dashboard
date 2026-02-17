"""
Device Manager Module
Handles device registration, tracking, and management for the IoT dashboard.
"""

import sqlite3
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
import threading

# Database path
DB_PATH = "iot_data.db"

# Thread-safe lock for database operations
db_lock = threading.Lock()


class DeviceManager:
    """Manages IoT devices in the dashboard."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_device_tables()
    
    def init_device_tables(self):
        """Initialize device-related database tables."""
        with db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Devices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    device_name TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    location TEXT,
                    capabilities TEXT,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen DATETIME,
                    status TEXT DEFAULT 'offline'
                )
            ''')
            
            # Check if sensor_data table exists before trying to alter it
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='sensor_data'
            """)
            if cursor.fetchone():
                # Table exists, check if device_id column exists
                cursor.execute("PRAGMA table_info(sensor_data)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'device_id' not in columns:
                    cursor.execute('ALTER TABLE sensor_data ADD COLUMN device_id TEXT')
            
            # Check if control_commands table exists before trying to alter it
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='control_commands'
            """)
            if cursor.fetchone():
                # Table exists, check if device_id column exists
                cursor.execute("PRAGMA table_info(control_commands)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'device_id' not in columns:
                    cursor.execute('ALTER TABLE control_commands ADD COLUMN device_id TEXT')
            
            conn.commit()
            conn.close()

    
    def register_device(self, device_id: str, device_name: str, device_type: str, 
                       location: str = "", capabilities: Dict = None) -> bool:
        """
        Register a new device or update existing device.
        
        Args:
            device_id: Unique device identifier
            device_name: Human-readable device name
            device_type: Type of device (ESP32, Arduino, RaspberryPi, etc.)
            location: Physical location of device
            capabilities: Dictionary of device capabilities
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                capabilities_json = json.dumps(capabilities or {})
                
                cursor.execute('''
                    INSERT OR REPLACE INTO devices 
                    (device_id, device_name, device_type, location, capabilities, last_seen, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (device_id, device_name, device_type, location, capabilities_json, 
                      datetime.now(), 'online'))
                
                conn.commit()
                conn.close()
                
                print(f"✓ Device registered: {device_name} ({device_id})")
                return True
        except Exception as e:
            print(f"Error registering device: {e}")
            return False
    
    def unregister_device(self, device_id: str) -> bool:
        """Remove a device from the system."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM devices WHERE device_id = ?', (device_id,))
                
                conn.commit()
                conn.close()
                
                print(f"✓ Device unregistered: {device_id}")
                return True
        except Exception as e:
            print(f"Error unregistering device: {e}")
            return False
    
    def update_device_status(self, device_id: str, status: str = 'online'):
        """Update device status and last seen timestamp."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE devices 
                    SET status = ?, last_seen = ?
                    WHERE device_id = ?
                ''', (status, datetime.now(), device_id))
                
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error updating device status: {e}")
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """Get device information by ID."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,))
                row = cursor.fetchone()
                
                conn.close()
                
                if row:
                    return {
                        'device_id': row[0],
                        'device_name': row[1],
                        'device_type': row[2],
                        'location': row[3],
                        'capabilities': json.loads(row[4]) if row[4] else {},
                        'registered_at': row[5],
                        'last_seen': row[6],
                        'status': row[7]
                    }
                return None
        except Exception as e:
            print(f"Error getting device: {e}")
            return None
    
    def get_all_devices(self) -> List[Dict]:
        """Get all registered devices."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM devices ORDER BY device_name')
                rows = cursor.fetchall()
                
                conn.close()
                
                devices = []
                for row in rows:
                    devices.append({
                        'device_id': row[0],
                        'device_name': row[1],
                        'device_type': row[2],
                        'location': row[3],
                        'capabilities': json.loads(row[4]) if row[4] else {},
                        'registered_at': row[5],
                        'last_seen': row[6],
                        'status': row[7]
                    })
                
                return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []
    
    def check_device_heartbeats(self, timeout_seconds: int = 60):
        """
        Check device heartbeats and mark devices as offline if not seen recently.
        
        Args:
            timeout_seconds: Number of seconds before marking device as offline
        """
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(seconds=timeout_seconds)
                
                cursor.execute('''
                    UPDATE devices 
                    SET status = 'offline'
                    WHERE last_seen < ? AND status = 'online'
                ''', (cutoff_time,))
                
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error checking device heartbeats: {e}")
    
    def get_device_sensor_data(self, device_id: str, hours: int = 24) -> List[Dict]:
        """Get sensor data for a specific device."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                cursor.execute('''
                    SELECT timestamp, temperature, humidity 
                    FROM sensor_data 
                    WHERE device_id = ? AND timestamp > ?
                    ORDER BY timestamp
                ''', (device_id, cutoff_time))
                
                rows = cursor.fetchall()
                conn.close()
                
                data = []
                for row in rows:
                    data.append({
                        'timestamp': row[0],
                        'temperature': row[1],
                        'humidity': row[2]
                    })
                
                return data
        except Exception as e:
            print(f"Error getting device sensor data: {e}")
            return []
    
    def get_device_stats(self, device_id: str) -> Dict:
        """Get statistics for a device."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get total data points
                cursor.execute('''
                    SELECT COUNT(*) FROM sensor_data WHERE device_id = ?
                ''', (device_id,))
                total_points = cursor.fetchone()[0]
                
                # Get latest reading
                cursor.execute('''
                    SELECT temperature, humidity, timestamp 
                    FROM sensor_data 
                    WHERE device_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (device_id,))
                latest = cursor.fetchone()
                
                conn.close()
                
                return {
                    'total_data_points': total_points,
                    'latest_temperature': latest[0] if latest else None,
                    'latest_humidity': latest[1] if latest else None,
                    'latest_timestamp': latest[2] if latest else None
                }
        except Exception as e:
            print(f"Error getting device stats: {e}")
            return {}


# Global device manager instance
device_manager = DeviceManager()

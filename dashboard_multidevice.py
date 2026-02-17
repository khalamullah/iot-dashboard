"""
IoT Cloud Dashboard - Multi-Device Support
A complete IoT dashboard with device management, MQTT integration, and real-time visualization.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import threading
import time
import sqlite3
import json
import os
from collections import deque, defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import device manager
from device_manager import device_manager

# ============================================================================
# CONFIGURATION
# ============================================================================

# MQTT Configuration (from environment variables)
MQTT_BROKER = os.getenv('MQTT_BROKER', 'broker.hivemq.com')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_CLIENT_ID = "iot_dashboard_" + str(int(time.time()))

# Database Configuration (from environment variables)
DB_PATH = os.getenv('DATABASE_URL', 'iot_data.db')
if DB_PATH.startswith('postgres://'):
    DB_PATH = DB_PATH.replace('postgres://', 'postgresql://', 1)

# Data Storage (in-memory for real-time display per device)
MAX_DATA_POINTS = 100
device_data = defaultdict(lambda: {
    'temperature': deque(maxlen=MAX_DATA_POINTS),
    'humidity': deque(maxlen=MAX_DATA_POINTS),
    'timestamps': deque(maxlen=MAX_DATA_POINTS)
})

# Thread-safe lock
data_lock = threading.Lock()

# Selected device for viewing
selected_device_id = None

# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_database():
    """Initialize SQLite database for historical data logging."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            device_id TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS control_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            command_type TEXT,
            command_value TEXT,
            device_id TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_sensor_data(temperature, humidity, device_id=None):
    """Log sensor data to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO sensor_data (temperature, humidity, device_id) VALUES (?, ?, ?)',
            (temperature, humidity, device_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database logging error: {e}")

def log_control_command(command_type, command_value, device_id=None):
    """Log control commands to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO control_commands (command_type, command_value, device_id) VALUES (?, ?, ?)',
            (command_type, str(command_value), device_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database logging error: {e}")

# ============================================================================
# MQTT CLIENT SETUP
# ============================================================================

mqtt_client = None
mqtt_connected = False

def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects."""
    global mqtt_connected
    if rc == 0:
        print("[OK] Connected to MQTT Broker!")
        mqtt_connected = True
        
        # Subscribe to all device topics
        client.subscribe("iot/dashboard/+/sensors")
        client.subscribe("iot/dashboard/+/status")
        client.subscribe("iot/dashboard/register")
        print("[OK] Subscribed to device topics")
    else:
        print(f"[ERROR] Failed to connect, return code {rc}")
        mqtt_connected = False

def on_message(client, userdata, msg):
    """Callback when MQTT message is received."""
    try:
        topic_parts = msg.topic.split('/')
        payload = json.loads(msg.payload.decode())
        
        # Handle device registration
        if msg.topic == "iot/dashboard/register":
            device_id = payload.get('device_id')
            device_name = payload.get('device_name')
            device_type = payload.get('device_type')
            location = payload.get('location', '')
            capabilities = payload.get('capabilities', {})
            
            device_manager.register_device(
                device_id, device_name, device_type, location, capabilities
            )
            print(f"[REGISTER] Device registered: {device_name} ({device_id})")
        
        # Handle sensor data
        elif len(topic_parts) >= 4 and topic_parts[3] == 'sensors':
            device_id = topic_parts[2]
            temperature = payload.get('temperature', 0)
            humidity = payload.get('humidity', 0)
            
            # Update in-memory data
            with data_lock:
                device_data[device_id]['timestamps'].append(datetime.now())
                device_data[device_id]['temperature'].append(temperature)
                device_data[device_id]['humidity'].append(humidity)
            
            # Log to database
            log_sensor_data(temperature, humidity, device_id)
            
            # Update device status
            device_manager.update_device_status(device_id, 'online')
            
            print(f"[DATA] [{device_id}] Temp={temperature}C, Humidity={humidity}%")
        
        # Handle status/heartbeat
        elif len(topic_parts) >= 4 and topic_parts[3] == 'status':
            device_id = topic_parts[2]
            status = payload.get('status', 'online')
            device_manager.update_device_status(device_id, status)
            
    except Exception as e:
        print(f"Error processing message: {e}")

def on_disconnect(client, userdata, rc):
    """Callback when MQTT client disconnects."""
    global mqtt_connected
    mqtt_connected = False
    print(f"[DISCONNECT] Disconnected from MQTT Broker (code {rc})")

def setup_mqtt():
    """Initialize and start MQTT client."""
    global mqtt_client
    
    mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect
    
    try:
        print(f"Connecting to MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"MQTT connection error: {e}")

def publish_control_command(device_id, command_type, value):
    """Publish control command to specific device."""
    if mqtt_client and mqtt_connected:
        payload = {
            "command": command_type,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        topic = f"iot/dashboard/{device_id}/control"
        mqtt_client.publish(topic, json.dumps(payload))
        log_control_command(command_type, value, device_id)
        print(f"[CONTROL] [{device_id}] {command_type} = {value}")
        return True
    else:
        print("[ERROR] MQTT not connected, cannot publish")
        return False

# Background task to check device heartbeats
def heartbeat_checker():
    """Periodically check device heartbeats."""
    while True:
        time.sleep(30)  # Check every 30 seconds
        device_manager.check_device_heartbeats(timeout_seconds=60)

# Start heartbeat checker thread
heartbeat_thread = threading.Thread(target=heartbeat_checker, daemon=True)
heartbeat_thread.start()

# ============================================================================
# DASH APPLICATION
# ============================================================================

# Initialize database
init_database()

# Initialize MQTT
setup_mqtt()

# Create Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

# Expose server for Gunicorn
server = app.server

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>IoT Cloud Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #0a0e27;
            }
            .status-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }
            .status-online {
                background-color: #00ff88;
                box-shadow: 0 0 8px #00ff88;
            }
            .status-offline {
                background-color: #ff4444;
                box-shadow: 0 0 8px #ff4444;
            }
            .metric-card {
                background: linear-gradient(135deg, #1e3a5f 0%, #2a5298 100%);
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transition: transform 0.2s;
            }
            .metric-card:hover {
                transform: translateY(-5px);
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: bold;
                color: #00ff88;
                text-shadow: 0 0 10px rgba(0,255,136,0.5);
            }
            .metric-label {
                font-size: 0.9rem;
                color: #adb5bd;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .device-card {
                cursor: pointer;
                transition: all 0.3s;
                border: 2px solid transparent;
            }
            .device-card:hover {
                border-color: #00ff88;
                transform: scale(1.02);
            }
            .device-card-selected {
                border-color: #00ff88;
                background-color: rgba(0,255,136,0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-cloud me-3"),
                "IoT Cloud Dashboard"
            ], className="text-center my-4 text-light"),
            html.Div(id='mqtt-status', className="text-center mb-4")
        ])
    ]),
    
    # Device Management Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H4([
                            html.I(className="fas fa-microchip me-2"),
                            "Device Management"
                        ], className="mb-0")),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-plus me-2"),
                                "Add Device"
                            ], id="add-device-btn", color="success", size="sm", className="float-end me-2"),
                            dbc.Button([
                                html.I(className="fas fa-sync me-2"),
                                "Refresh"
                            ], id="refresh-devices-btn", color="info", size="sm", className="float-end")
                        ], width="auto")
                    ])
                ]),
                dbc.CardBody([
                    html.Div(id='device-list')
                ])
            ], className="shadow-lg mb-4")
        ])
    ]),
    
    # Current Metrics (for selected device)
    html.Div(id='device-metrics-section'),
    
    # Real-time Charts
    html.Div(id='device-charts-section'),
    
    # Control Panel
    html.Div(id='device-control-section'),
    
    # Add Device Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add New Device")),
        dbc.ModalBody([
            dbc.Label("Device ID"),
            dbc.Input(id="new-device-id", placeholder="e.g., esp32_001", className="mb-3"),
            dbc.Label("Device Name"),
            dbc.Input(id="new-device-name", placeholder="e.g., Living Room Sensor", className="mb-3"),
            dbc.Label("Device Type"),
            dbc.Select(
                id="new-device-type",
                options=[
                    {"label": "ESP32", "value": "ESP32"},
                    {"label": "Arduino", "value": "Arduino"},
                    {"label": "Raspberry Pi", "value": "RaspberryPi"},
                    {"label": "Other", "value": "Other"}
                ],
                className="mb-3"
            ),
            dbc.Label("Location"),
            dbc.Input(id="new-device-location", placeholder="e.g., Living Room", className="mb-3"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-add-device", color="secondary", className="me-2"),
            dbc.Button("Add Device", id="confirm-add-device", color="success")
        ])
    ], id="add-device-modal", is_open=False),
    
    # Store for selected device
    dcc.Store(id='selected-device-store', data=None),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every 1 second
        n_intervals=0
    ),
    
], fluid=True, className="py-4")

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    Output('mqtt-status', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_mqtt_status(n):
    """Update MQTT connection status indicator."""
    if mqtt_connected:
        return html.Div([
            html.Span(className="status-indicator status-online"),
            html.Span("Connected to MQTT Broker", className="text-success fw-bold")
        ])
    else:
        return html.Div([
            html.Span(className="status-indicator status-offline"),
            html.Span("Disconnected from MQTT Broker", className="text-danger fw-bold")
        ])

@app.callback(
    Output('device-list', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('refresh-devices-btn', 'n_clicks')],
    State('selected-device-store', 'data')
)
def update_device_list(n, refresh_clicks, selected_device):
    """Update the list of devices."""
    devices = device_manager.get_all_devices()
    
    if not devices:
        return dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            "No devices registered yet. Add a device or wait for auto-registration from ESP32 devices."
        ], color="info")
    
    device_cards = []
    for device in devices:
        is_selected = selected_device == device['device_id']
        status_class = "status-online" if device['status'] == 'online' else "status-offline"
        card_class = "device-card device-card-selected" if is_selected else "device-card"
        
        device_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Span(className=f"status-indicator {status_class}"),
                            html.Strong(device['device_name'], className="fs-5")
                        ]),
                        html.Hr(),
                        html.Div([
                            html.I(className="fas fa-microchip me-2"),
                            html.Small(f"Type: {device['device_type']}", className="text-muted")
                        ]),
                        html.Div([
                            html.I(className="fas fa-map-marker-alt me-2"),
                            html.Small(f"Location: {device['location'] or 'Not set'}", className="text-muted")
                        ]),
                        html.Div([
                            html.I(className="fas fa-fingerprint me-2"),
                            html.Small(f"ID: {device['device_id']}", className="text-muted")
                        ]),
                    ])
                ], className=card_class, id={'type': 'device-card', 'index': device['device_id']})
            ], width=12, md=6, lg=4, className="mb-3")
        )
    
    return dbc.Row(device_cards)

@app.callback(
    Output('selected-device-store', 'data'),
    Input({'type': 'device-card', 'index': ALL}, 'n_clicks'),
    State('selected-device-store', 'data'),
    prevent_initial_call=True
)
def select_device(n_clicks, current_selection):
    """Handle device selection."""
    ctx = callback_context
    if not ctx.triggered:
        return current_selection
    
    trigger = ctx.triggered[0]
    if trigger['value'] is None:
        return current_selection
    
    # Extract device ID from trigger
    prop_id = json.loads(trigger['prop_id'].split('.')[0])
    device_id = prop_id['index']
    
    return device_id

@app.callback(
    [Output('device-metrics-section', 'children'),
     Output('device-charts-section', 'children'),
     Output('device-control-section', 'children')],
    [Input('selected-device-store', 'data'),
     Input('interval-component', 'n_intervals')]
)
def update_device_sections(device_id, n):
    """Update metrics, charts, and controls for selected device."""
    if not device_id:
        return [
            dbc.Alert("Select a device to view details", color="secondary", className="text-center"),
            None,
            None
        ]
    
    device = device_manager.get_device(device_id)
    if not device:
        return [
            dbc.Alert("Device not found", color="danger"),
            None,
            None
        ]
    
    # Get latest data
    with data_lock:
        if device_id in device_data and len(device_data[device_id]['temperature']) > 0:
            temp = device_data[device_id]['temperature'][-1]
            hum = device_data[device_id]['humidity'][-1]
            last_time = device_data[device_id]['timestamps'][-1]
            count = len(device_data[device_id]['temperature'])
        else:
            temp = None
            hum = None
            last_time = None
            count = 0
    
    # Metrics Section
    metrics = dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("🌡️ Temperature", className="metric-label"),
                html.Div(f"{temp:.1f}°C" if temp is not None else "-- °C", className="metric-value")
            ], className="metric-card")
        ], width=6, lg=3),
        
        dbc.Col([
            html.Div([
                html.Div("💧 Humidity", className="metric-label"),
                html.Div(f"{hum:.1f}%" if hum is not None else "-- %", className="metric-value")
            ], className="metric-card")
        ], width=6, lg=3),
        
        dbc.Col([
            html.Div([
                html.Div("📊 Data Points", className="metric-label"),
                html.Div(str(count), className="metric-value")
            ], className="metric-card")
        ], width=6, lg=3),
        
        dbc.Col([
            html.Div([
                html.Div("⏰ Last Update", className="metric-label"),
                html.Div(last_time.strftime("%H:%M:%S") if last_time else "--:--:--", 
                        className="metric-value", style={'fontSize': '1.2rem'})
            ], className="metric-card")
        ], width=6, lg=3),
    ], className="mb-4")
    
    # Charts Section
    with data_lock:
        if device_id in device_data and len(device_data[device_id]['timestamps']) > 0:
            times = list(device_data[device_id]['timestamps'])
            temps = list(device_data[device_id]['temperature'])
            hums = list(device_data[device_id]['humidity'])
        else:
            times = []
            temps = []
            hums = []
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times, y=temps,
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=times, y=hums,
        mode='lines+markers',
        name='Humidity',
        line=dict(color='#4ecdc4', width=3),
        marker=dict(size=6),
        yaxis='y2'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.2)',
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title='Time', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title='Temperature (°C)', showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='left'),
        yaxis2=dict(title='Humidity (%)', overlaying='y', side='right', showgrid=False),
        margin=dict(l=50, r=50, t=30, b=50)
    )
    
    charts = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4(f"📈 Real-Time Data - {device['device_name']}", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(figure=fig, config={'displayModeBar': False})
                ])
            ], className="shadow-lg")
        ])
    ], className="mb-4")
    
    # Control Section
    controls = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4(f"🎛️ Control Panel - {device['device_name']}", className="mb-0")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("💡 LED Control", className="fw-bold mb-2"),
                            dbc.ButtonGroup([
                                dbc.Button("ON", id={'type': 'led-on', 'index': device_id}, 
                                          color="success", n_clicks=0),
                                dbc.Button("OFF", id={'type': 'led-off', 'index': device_id}, 
                                          color="danger", n_clicks=0),
                            ], className="w-100")
                        ], width=12, md=6, className="mb-3"),
                        
                        dbc.Col([
                            html.Label("🌀 Fan Speed Control", className="fw-bold mb-2"),
                            dcc.Slider(
                                id={'type': 'fan-speed', 'index': device_id},
                                min=0, max=100, step=10, value=0,
                                marks={i: f"{i}%" for i in range(0, 101, 20)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], width=12, md=6, className="mb-3"),
                    ]),
                    html.Hr(),
                    html.Div(id='control-feedback')
                ])
            ], className="shadow-lg")
        ])
    ], className="mb-4")
    
    return metrics, charts, controls

@app.callback(
    Output('control-feedback', 'children'),
    [Input({'type': 'led-on', 'index': ALL}, 'n_clicks'),
     Input({'type': 'led-off', 'index': ALL}, 'n_clicks'),
     Input({'type': 'fan-speed', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def handle_controls(led_on, led_off, fan_speed):
    """Handle control commands."""
    ctx = callback_context
    if not ctx.triggered:
        return ""
    
    trigger = ctx.triggered[0]
    if trigger['value'] is None:
        return ""
    
    prop_id = json.loads(trigger['prop_id'].split('.')[0])
    device_id = prop_id['index']
    control_type = prop_id['type']
    
    if control_type == 'led-on':
        success = publish_control_command(device_id, "LED", "ON")
        return dbc.Alert("✓ LED turned ON", color="success", dismissable=True, duration=3000) if success else dbc.Alert("✗ Failed", color="danger", dismissable=True, duration=3000)
    
    elif control_type == 'led-off':
        success = publish_control_command(device_id, "LED", "OFF")
        return dbc.Alert("✓ LED turned OFF", color="success", dismissable=True, duration=3000) if success else dbc.Alert("✗ Failed", color="danger", dismissable=True, duration=3000)
    
    elif control_type == 'fan-speed':
        value = trigger['value']
        success = publish_control_command(device_id, "FAN_SPEED", value)
        return dbc.Alert(f"✓ Fan speed set to {value}%", color="info", dismissable=True, duration=3000) if success else dbc.Alert("✗ Failed", color="danger", dismissable=True, duration=3000)
    
    return ""

@app.callback(
    Output("add-device-modal", "is_open"),
    [Input("add-device-btn", "n_clicks"),
     Input("confirm-add-device", "n_clicks"),
     Input("cancel-add-device", "n_clicks")],
    State("add-device-modal", "is_open"),
)
def toggle_add_device_modal(add_click, confirm_click, cancel_click, is_open):
    """Toggle add device modal."""
    if add_click or confirm_click or cancel_click:
        return not is_open
    return is_open

@app.callback(
    Output("new-device-id", "value"),
    Input("confirm-add-device", "n_clicks"),
    [State("new-device-id", "value"),
     State("new-device-name", "value"),
     State("new-device-type", "value"),
     State("new-device-location", "value")],
    prevent_initial_call=True
)
def add_new_device(n_clicks, device_id, device_name, device_type, location):
    """Add a new device manually."""
    if n_clicks and device_id and device_name and device_type:
        device_manager.register_device(
            device_id, device_name, device_type, location or "", {}
        )
        return ""  # Clear the input
    return device_id

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Get configuration from environment
    PORT = int(os.getenv('PORT', 8050))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    
    print("\n" + "="*60)
    print("IoT Cloud Dashboard Starting...")
    print("="*60)
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Database: {DB_PATH}")
    print(f"Dashboard: http://{HOST}:{PORT}")
    print(f"Debug Mode: {DEBUG}")
    print("="*60 + "\n")
    
    app.run_server(debug=DEBUG, host=HOST, port=PORT)

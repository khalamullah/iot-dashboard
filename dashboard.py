"""
IoT Cloud Dashboard - Production-Ready Application
A complete IoT dashboard with MQTT integration, real-time visualization, and data logging.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import threading
import time
import sqlite3
import json
from collections import deque

# ============================================================================
# CONFIGURATION
# ============================================================================

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"  # Public broker for testing
MQTT_PORT = 1883
MQTT_TOPIC_SENSOR = "iot/dashboard/sensors"
MQTT_TOPIC_CONTROL = "iot/dashboard/control"
MQTT_CLIENT_ID = "iot_dashboard_" + str(int(time.time()))

# Database Configuration
DB_PATH = "iot_data.db"

# Data Storage (in-memory for real-time display)
MAX_DATA_POINTS = 100
temperature_data = deque(maxlen=MAX_DATA_POINTS)
humidity_data = deque(maxlen=MAX_DATA_POINTS)
timestamps = deque(maxlen=MAX_DATA_POINTS)

# Thread-safe lock
data_lock = threading.Lock()

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
            humidity REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS control_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            command_type TEXT,
            command_value TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_sensor_data(temperature, humidity):
    """Log sensor data to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)',
            (temperature, humidity)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database logging error: {e}")

def log_control_command(command_type, command_value):
    """Log control commands to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO control_commands (command_type, command_value) VALUES (?, ?)',
            (command_type, str(command_value))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database logging error: {e}")

def get_historical_data(hours=24):
    """Retrieve historical data from database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cursor.execute('''
            SELECT timestamp, temperature, humidity 
            FROM sensor_data 
            WHERE timestamp > ?
            ORDER BY timestamp
        ''', (cutoff_time,))
        
        data = cursor.fetchall()
        conn.close()
        return data
    except Exception as e:
        print(f"Database query error: {e}")
        return []

# ============================================================================
# MQTT CLIENT SETUP
# ============================================================================

mqtt_client = None
mqtt_connected = False

def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects."""
    global mqtt_connected
    if rc == 0:
        print("✓ Connected to MQTT Broker!")
        mqtt_connected = True
        client.subscribe(MQTT_TOPIC_SENSOR)
        print(f"✓ Subscribed to topic: {MQTT_TOPIC_SENSOR}")
    else:
        print(f"✗ Failed to connect, return code {rc}")
        mqtt_connected = False

def on_message(client, userdata, msg):
    """Callback when MQTT message is received."""
    try:
        payload = json.loads(msg.payload.decode())
        temperature = payload.get('temperature', 0)
        humidity = payload.get('humidity', 0)
        
        # Update in-memory data
        with data_lock:
            timestamps.append(datetime.now())
            temperature_data.append(temperature)
            humidity_data.append(humidity)
        
        # Log to database
        log_sensor_data(temperature, humidity)
        
        print(f"📊 Received: Temp={temperature}°C, Humidity={humidity}%")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_disconnect(client, userdata, rc):
    """Callback when MQTT client disconnects."""
    global mqtt_connected
    mqtt_connected = False
    print(f"✗ Disconnected from MQTT Broker (code {rc})")

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

def publish_control_command(command_type, value):
    """Publish control command to MQTT broker."""
    if mqtt_client and mqtt_connected:
        payload = {
            "command": command_type,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        mqtt_client.publish(MQTT_TOPIC_CONTROL, json.dumps(payload))
        log_control_command(command_type, value)
        print(f"📤 Published: {command_type} = {value}")
        return True
    else:
        print("✗ MQTT not connected, cannot publish")
        return False

# ============================================================================
# DASH APPLICATION
# ============================================================================

# Initialize database
init_database()

# Initialize MQTT
setup_mqtt()

# Create Dash app with dark theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True
)

# Custom CSS for better styling
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
            .status-connected {
                background-color: #00ff88;
                box-shadow: 0 0 8px #00ff88;
            }
            .status-disconnected {
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
    
    # Current Metrics Cards
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div("🌡️ Temperature", className="metric-label"),
                html.Div(id='current-temperature', className="metric-value")
            ], className="metric-card")
        ], width=6, lg=3),
        
        dbc.Col([
            html.Div([
                html.Div("💧 Humidity", className="metric-label"),
                html.Div(id='current-humidity', className="metric-value")
            ], className="metric-card")
        ], width=6, lg=3),
        
        dbc.Col([
            html.Div([
                html.Div("📊 Data Points", className="metric-label"),
                html.Div(id='data-count', className="metric-value")
            ], className="metric-card")
        ], width=6, lg=3),
        
        dbc.Col([
            html.Div([
                html.Div("⏰ Last Update", className="metric-label"),
                html.Div(id='last-update', className="metric-value", style={'fontSize': '1.2rem'})
            ], className="metric-card")
        ], width=6, lg=3),
    ], className="mb-4"),
    
    # Real-time Charts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("📈 Real-Time Sensor Data", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='live-graph', config={'displayModeBar': False})
                ])
            ], className="shadow-lg")
        ])
    ], className="mb-4"),
    
    # Control Panel
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("🎛️ Device Control Panel", className="mb-0")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("💡 LED Control", className="fw-bold mb-2"),
                            dbc.ButtonGroup([
                                dbc.Button("ON", id="led-on-btn", color="success", n_clicks=0),
                                dbc.Button("OFF", id="led-off-btn", color="danger", n_clicks=0),
                            ], className="w-100")
                        ], width=12, md=6, className="mb-3"),
                        
                        dbc.Col([
                            html.Label("🌀 Fan Speed Control", className="fw-bold mb-2"),
                            dcc.Slider(
                                id='fan-speed-slider',
                                min=0,
                                max=100,
                                step=10,
                                value=0,
                                marks={i: f"{i}%" for i in range(0, 101, 20)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], width=12, md=6, className="mb-3"),
                    ]),
                    
                    html.Hr(),
                    
                    html.Div(id='control-feedback', className="mt-3")
                ])
            ], className="shadow-lg")
        ])
    ], className="mb-4"),
    
    # Historical Data Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H4("📜 Historical Data", className="mb-0")),
                        dbc.Col([
                            dbc.Button("Load Last 24 Hours", id="load-history-btn", 
                                      color="info", size="sm", className="float-end")
                        ], width="auto")
                    ])
                ]),
                dbc.CardBody([
                    dcc.Graph(id='historical-graph', config={'displayModeBar': True})
                ])
            ], className="shadow-lg")
        ])
    ], className="mb-4"),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every 1 second
        n_intervals=0
    ),
    
    # Store for control feedback
    dcc.Store(id='control-store')
    
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
            html.Span(className="status-indicator status-connected"),
            html.Span("Connected to MQTT Broker", className="text-success fw-bold")
        ])
    else:
        return html.Div([
            html.Span(className="status-indicator status-disconnected"),
            html.Span("Disconnected from MQTT Broker", className="text-danger fw-bold")
        ])

@app.callback(
    [Output('current-temperature', 'children'),
     Output('current-humidity', 'children'),
     Output('data-count', 'children'),
     Output('last-update', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    """Update current metric displays."""
    with data_lock:
        if len(temperature_data) > 0:
            temp = f"{temperature_data[-1]:.1f}°C"
            hum = f"{humidity_data[-1]:.1f}%"
            count = str(len(temperature_data))
            last = timestamps[-1].strftime("%H:%M:%S")
        else:
            temp = "-- °C"
            hum = "-- %"
            count = "0"
            last = "--:--:--"
    
    return temp, hum, count, last

@app.callback(
    Output('live-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_live_graph(n):
    """Update real-time graph with latest data."""
    with data_lock:
        if len(timestamps) > 0:
            times = list(timestamps)
            temps = list(temperature_data)
            hums = list(humidity_data)
        else:
            times = []
            temps = []
            hums = []
    
    fig = go.Figure()
    
    # Temperature trace
    fig.add_trace(go.Scatter(
        x=times,
        y=temps,
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=6)
    ))
    
    # Humidity trace
    fig.add_trace(go.Scatter(
        x=times,
        y=hums,
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
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            title='Time',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title='Temperature (°C)',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            side='left'
        ),
        yaxis2=dict(
            title='Humidity (%)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        margin=dict(l=50, r=50, t=30, b=50)
    )
    
    return fig

@app.callback(
    Output('control-feedback', 'children'),
    [Input('led-on-btn', 'n_clicks'),
     Input('led-off-btn', 'n_clicks'),
     Input('fan-speed-slider', 'value')],
    prevent_initial_call=True
)
def handle_controls(led_on_clicks, led_off_clicks, fan_speed):
    """Handle control panel interactions."""
    ctx = callback_context
    
    if not ctx.triggered:
        return ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'led-on-btn':
        success = publish_control_command("LED", "ON")
        if success:
            return dbc.Alert("✓ LED turned ON", color="success", dismissable=True, duration=3000)
        else:
            return dbc.Alert("✗ Failed to send command", color="danger", dismissable=True, duration=3000)
    
    elif trigger_id == 'led-off-btn':
        success = publish_control_command("LED", "OFF")
        if success:
            return dbc.Alert("✓ LED turned OFF", color="success", dismissable=True, duration=3000)
        else:
            return dbc.Alert("✗ Failed to send command", color="danger", dismissable=True, duration=3000)
    
    elif trigger_id == 'fan-speed-slider':
        success = publish_control_command("FAN_SPEED", fan_speed)
        if success:
            return dbc.Alert(f"✓ Fan speed set to {fan_speed}%", color="info", dismissable=True, duration=3000)
        else:
            return dbc.Alert("✗ Failed to send command", color="danger", dismissable=True, duration=3000)
    
    return ""

@app.callback(
    Output('historical-graph', 'figure'),
    Input('load-history-btn', 'n_clicks'),
    prevent_initial_call=True
)
def load_historical_data(n_clicks):
    """Load and display historical data from database."""
    data = get_historical_data(hours=24)
    
    if not data:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No historical data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray")
        )
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.2)',
            height=400
        )
        return fig
    
    timestamps_hist = [datetime.fromisoformat(row[0]) for row in data]
    temps_hist = [row[1] for row in data]
    hums_hist = [row[2] for row in data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timestamps_hist,
        y=temps_hist,
        mode='lines',
        name='Temperature',
        line=dict(color='#ff6b6b', width=2),
        fill='tozeroy',
        fillcolor='rgba(255,107,107,0.1)'
    ))
    
    fig.add_trace(go.Scatter(
        x=timestamps_hist,
        y=hums_hist,
        mode='lines',
        name='Humidity',
        line=dict(color='#4ecdc4', width=2),
        fill='tozeroy',
        fillcolor='rgba(78,205,196,0.1)',
        yaxis='y2'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.2)',
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            title='Time',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title='Temperature (°C)',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            side='left'
        ),
        yaxis2=dict(
            title='Humidity (%)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        margin=dict(l=50, r=50, t=30, b=50)
    )
    
    return fig

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 IoT Cloud Dashboard Starting...")
    print("="*60)
    print(f"📡 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"📊 Database: {DB_PATH}")
    print(f"🌐 Dashboard will be available at: http://127.0.0.1:8050")
    print("="*60 + "\n")
    
    app.run_server(debug=True, host='0.0.0.0', port=8050)
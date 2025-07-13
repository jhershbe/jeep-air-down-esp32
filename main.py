# main.py - ESP32 MicroPython Captive Portal and Web Interface using Microdot

import network
import time
import machine
import ujson

# Setpoint persistence helpers
SETPOINTS_FILE = 'setpoints.json'

def load_setpoints():
    try:
        with open(SETPOINTS_FILE) as f:
            s = ujson.load(f)
            return s.get('setpoint_onroad', 32), s.get('setpoint_offroad', 14)
    except Exception as e:
        print('Error loading setpoints:', e)
        return 32, 14

def save_setpoints(s_onroad, s_offroad):
    with open(SETPOINTS_FILE, 'w') as f:
        ujson.dump({'setpoint_onroad': float(s_onroad), 'setpoint_offroad': float(s_offroad)}, f)

# Pin definitions (customize as needed)
relay_pins = [12, 13, 14, 25]
relay_outputs = [machine.Pin(pin, machine.Pin.OUT) for pin in relay_pins]
compressed_air_relay = relay_outputs[0]
vent_air_relay = relay_outputs[1]
pressure_adc = machine.ADC(machine.Pin(32))
pressure_adc.atten(machine.ADC.ATTN_2_5DB)

# WiFi Access Point Setup
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP32-AirCtrl', password='esp32pass', authmode=network.AUTH_WPA_WPA2_PSK)

# Wait for AP to be active
while not ap.active():
    time.sleep(0.1)
print('AP active, IP:', ap.ifconfig()[0])

# Now import Microdot and asyncio (after WiFi is initialized)
from microdot import Microdot, Response
import uasyncio as asyncio

# Set up Microdot
app = Microdot()
Response.default_content_type = 'application/json'

# --- Command state tracking dictionary ---
command_state = {
    'air_up': {'running': False, 'cancel': False, 'task': None},
    'air_down': {'running': False, 'cancel': False, 'task': None}
}

# Simple captive portal handler
@app.route('/')
def index(request):
    return Response(body="""
<html>
<head>
    <title>ESP32 Air Control</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <meta name='apple-mobile-web-app-capable' content='yes'>
    <meta name='apple-mobile-web-app-title' content='ESP32 AirCtrl'>
    <link rel='stylesheet' href='/style.css'>
</head>
<body>
    <div class='container'>
        <h2>Air Pressure Sensor</h2>
        <span class='pressure-value' id='pressure'>--</span>
        <span class='psi-label'>PSI</span>
        <div class='command-buttons'>
            <button class='air-up' onclick='airUp()'>Air Up</button>
            <button class='air-down' onclick='airDown()'>Air Down</button>
        </div>
        <div class='setpoints'>
            <label for='setpoint_onroad'>On Road (PSI):</label>
            <input type='number' id='setpoint_onroad' min='0' max='300' step='0.1'>
            <label for='setpoint_offroad'>Off Road (PSI):</label>
            <input type='number' id='setpoint_offroad' min='0' max='300' step='0.1'>
            <button class='save-setpoints' onclick='saveSetpoints()'>Save Setpoints</button>
        </div>

    </div>
    <script src='/script.js'></script>
</body>
</html>
""", headers={'Content-Type': 'text/html'})

@app.route('/get_setpoints')
def get_setpoints(request):
    s_onroad, s_offroad = load_setpoints()
    return {'setpoint_onroad': s_onroad, 'setpoint_offroad': s_offroad}

@app.route('/set_setpoints', methods=['POST'])
def set_setpoints(request):
    data = request.json
    save_setpoints(data.get('setpoint_onroad', 0), data.get('setpoint_offroad', 0))
    return {'status': 'ok'}

# --- Command state tracking dictionary ---
command_state = {
    'air_up': {'running': False, 'cancel': False, 'task': None},
    'air_down': {'running': False, 'cancel': False, 'task': None}
}

# RESTful Air Command API

# Air Up command API
@app.route('/air_up', methods=['POST', 'GET'])
def air_up(request):
    """RESTful endpoint for air up operations"""
    # Get action from URL parameters (default to 'start')
    action = request.args.get('action', 'start')
    cmd = 'air_up'
    
    if action == 'status':
        # Status query doesn't change state
        is_running = command_state[cmd]['running']
        return {
            'status': 'running' if is_running else 'idle',
            'command': cmd,
            'time': time.time() - last_command_time.get(cmd, 0) if is_running else 0
        }
    
    elif action == 'start':
        # Start command
        if not command_state[cmd]['running']:
            command_state[cmd]['running'] = True
            command_state[cmd]['cancel'] = False
            last_command_time[cmd] = time.time()
            
            # Store start time
            command_state[cmd]['start_time'] = time.time()
            
            # Activate hardware
            print(f"{cmd} started")
            # TODO: Add hardware control
            # relay_outputs[0].value(1)  # Turn on air compressor relay
            
            # Create async task for long-running operations
            # We'll implement this after confirming basic functionality works
            
            return {
                'status': 'started',
                'command': cmd,
                'message': 'Air up operation started'
            }
        else:
            return {
                'status': 'already_running',
                'command': cmd,
                'message': 'Air up operation already in progress'
            }
    
    elif action == 'cancel':
        # Cancel command
        if command_state[cmd]['running']:
            command_state[cmd]['cancel'] = True
            command_state[cmd]['running'] = False
            
            # Deactivate hardware
            print(f"{cmd} cancelled")
            # TODO: Add hardware control
            # compressed_air_relay.value(0)  # Turn off air compressor relay
            
            # Clean up timers
            if cmd in last_command_time:
                del last_command_time[cmd]
                
            return {
                'status': 'cancelled',
                'command': cmd,
                'message': 'Air up operation cancelled'
            }
        else:
            return {
                'status': 'not_running',
                'command': cmd,
                'message': 'No air up operation in progress'
            }
    
    # Invalid action
    return {
        'status': 'error',
        'command': cmd,
        'message': f"Unknown action: {action}"
    }

# Air Down command API
@app.route('/air_down', methods=['POST', 'GET'])
def air_down(request):
    """RESTful endpoint for air down operations"""
    # Get action from URL parameters (default to 'start')
    action = request.args.get('action', 'start')
    cmd = 'air_down'
    
    if action == 'status':
        # Status query doesn't change state
        is_running = command_state[cmd]['running']
        return {
            'status': 'running' if is_running else 'idle',
            'command': cmd,
            'time': time.time() - last_command_time.get(cmd, 0) if is_running else 0
        }
    
    elif action == 'start':
        # Start command
        if not command_state[cmd]['running']:
            command_state[cmd]['running'] = True
            command_state[cmd]['cancel'] = False
            last_command_time[cmd] = time.time()
            
            # Store start time
            command_state[cmd]['start_time'] = time.time()
            
            # Activate hardware
            print(f"{cmd} started")
            # TODO: Add hardware control
            # relay_outputs[1].value(1)  # Turn on release valve relay
            
            # Create async task for long-running operations
            # We'll implement this after confirming basic functionality works
            
            return {
                'status': 'started',
                'command': cmd,
                'message': 'Air down operation started'
            }
        else:
            return {
                'status': 'already_running',
                'command': cmd,
                'message': 'Air down operation already in progress'
            }
    
    elif action == 'cancel':
        # Cancel command
        if command_state[cmd]['running']:
            command_state[cmd]['cancel'] = True
            command_state[cmd]['running'] = False
            
            # Deactivate hardware
            print(f"{cmd} cancelled")
            # TODO: Add hardware control
            # vent_air_relay.value(0)  # Turn off release valve relay
            
            # Clean up timers
            if cmd in last_command_time:
                del last_command_time[cmd]
                
            return {
                'status': 'cancelled',
                'command': cmd,
                'message': 'Air down operation cancelled'
            }
        else:
            return {
                'status': 'not_running',
                'command': cmd,
                'message': 'No air down operation in progress'
            }
    
    # Invalid action
    return {
        'status': 'error',
        'command': cmd,
        'message': f"Unknown action: {action}"
    }

@app.route('/pressure')
def get_pressure(request):
    # Average 256 readings for noise reduction
    pres_raw = 0
    for _ in range(256):
        pres_raw += pressure_adc.read_uv() if hasattr(pressure_adc, 'read_uv') else pressure_adc.read()
    pres_raw = pres_raw >> 8
    pres_psi = (pres_raw - 5000000) * 0.00005 if hasattr(pressure_adc, 'read_uv') else pres_raw * 0.001  # fallback
    if pres_psi < 0.0:
        pres_psi = 0.0
    return {"pressure": round(pres_psi, 2)}

# Captive portal redirect for common OS probes
def captive_portal_page():
    # Return the same response as the main index route
    return index(None)

@app.route('/generate_204')
@app.route('/fwlink')
@app.route('/hotspot-detect.html')
@app.route('/ncsi.txt')
def captive_redirect(request):
    # Serve the captive portal page directly
    return captive_portal_page()

# Static file routes - Must come BEFORE catch-all route
@app.route('/style.css')
def style_css(request):
    with open('style.css') as f:
        css = f.read()
    return Response(body=css, headers={'Content-Type': 'text/css'})

@app.route('/script.js')
def script_js(request):
    with open('script.js') as f:
        js = f.read()
    return Response(body=js, headers={'Content-Type': 'application/javascript'})

# Catch-all: serve the captive portal page for all unknown URLs
@app.route('/<path:path>')
def catch_all(request, path):
    return captive_portal_page()

# Configuration for command execution
COMMAND_DURATION = 10  # seconds for a command to complete
last_command_time = {}  # Tracks when commands started (for backward compatibility)

async def check_command_status():
    """Background task that monitors command state and handles auto-completion"""
    while True:
        current_time = time.time()
        
        # Check both commands
        for cmd in ['air_up', 'air_down']:
            # Check if command is running (two ways to check for compatibility)
            is_running = command_state[cmd]['running']
            
            # Safely access start_time (may not exist in older command_state structures)
            start_time = 0
            if 'start_time' in command_state[cmd]:
                start_time = command_state[cmd]['start_time']
                
            has_start_time = cmd in last_command_time or start_time > 0
            
            if is_running and has_start_time:
                # Get elapsed time (support both tracking methods)
                start_time = 0
                if 'start_time' in command_state[cmd]:
                    start_time = command_state[cmd]['start_time']
                    
                # Fall back to legacy timing if needed
                if start_time == 0 and cmd in last_command_time:
                    start_time = last_command_time[cmd]
                
                elapsed = current_time - start_time
                
                # Check if command should auto-complete
                if elapsed > COMMAND_DURATION:
                    print(f"{cmd} auto-completed after {elapsed:.1f} seconds")
                    
                    # Reset command state
                    command_state[cmd]['running'] = False
                    command_state[cmd]['cancel'] = False
                    
                    # Safely update start_time if it exists
                    if 'start_time' in command_state[cmd]:
                        command_state[cmd]['start_time'] = 0
                    
                    # Clean up legacy tracking
                    if cmd in last_command_time:
                        del last_command_time[cmd]
                        
                    # TODO: Turn off hardware here
                    # if cmd == 'air_up':
                    #     compressed_air_relay.value(0)  # Turn off air compressor
                    # elif cmd == 'air_down':
                    #     vent_air_relay.value(0)  # Turn off release valve
        
        # Check once per second
        await asyncio.sleep(1)

# Run the app (non-blocking, with asyncio)
async def main():
    print('Starting Microdot server (asyncio mode)...')
    # Start the command status checker in the background
    asyncio.create_task(check_command_status())
    # Start the server
    await app.start_server(host='0.0.0.0', port=80)

try:
    print('Starting async event loop...')
    asyncio.run(main())
    print('Microdot server started!')
except Exception as e:
    import sys
    sys.print_exception(e)
    print('Error starting server:', e)

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
pressure_adc.atten(machine.ADC.ATTN_11DB)

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
    <link rel='apple-touch-icon' href='/icon.png'>
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
            # Initialize command state
            command_state[cmd]['running'] = True
            command_state[cmd]['cancel'] = False
            command_state[cmd]['start_time'] = time.time()
            last_command_time[cmd] = time.time()
            
            # Load the on-road pressure setpoint for air_up
            s_onroad, s_offroad = load_setpoints()
            target_psi = float(s_onroad)
            command_state[cmd]['target_psi'] = target_psi
            
            # Create async task for pressure adjustment
            print(f"{cmd} started with target {target_psi} PSI")
            asyncio.create_task(adjust_pressure(cmd, target_psi))
            
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
            # Initialize command state
            command_state[cmd]['running'] = True
            command_state[cmd]['cancel'] = False
            command_state[cmd]['start_time'] = time.time()
            last_command_time[cmd] = time.time()
            
            # Load the off-road pressure setpoint for air_down
            s_onroad, s_offroad = load_setpoints()
            target_psi = float(s_offroad)
            command_state[cmd]['target_psi'] = target_psi
            
            # Create async task for pressure adjustment
            print(f"{cmd} started with target {target_psi} PSI")
            asyncio.create_task(adjust_pressure(cmd, target_psi))
            
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

# Utility function for internal pressure reading
def read_pressure():
    """Read pressure sensor and return PSI value"""
    # Average 16 readings for noise reduction
    pres_raw = 0
    for _ in range(16):
        pres_raw += pressure_adc.read_uv()
    pres_raw = pres_raw >> 4
    pres_psi = (pres_raw - 500000) * 0.00005
    if pres_psi < 0.0:
        pres_psi = 0.0
    return pres_psi

async def wait_for_stable_pressure(max_wait_time=5.0, stability_threshold=0.5):
    """Wait for pressure reading to stabilize, returning stable pressure value
    
    Args:
        max_wait_time: Maximum time to wait in seconds
        stability_threshold: Consider stable if change is less than this in PSI
        
    Returns:
        Stable pressure reading
    """
    start_time = time.time()
    last_pressure = read_pressure()
    last_check_time = start_time
    
    # Initial reading
    await asyncio.sleep(0.2)
    
    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        # Don't wait longer than max_wait_time
        if elapsed >= max_wait_time:
            return read_pressure()
        
        # Check every 250ms
        if current_time - last_check_time >= 0.25:
            current_pressure = read_pressure()
            time_diff = current_time - last_check_time
            pressure_change_rate = abs(current_pressure - last_pressure) / time_diff
            
            # If change rate is less than threshold PSI per second, consider stable
            if pressure_change_rate < stability_threshold:
                return current_pressure
            
            # Update for next check
            last_pressure = current_pressure
            last_check_time = current_time
        
        # Yield to other tasks briefly
        await asyncio.sleep(0.1)

@app.route('/pressure')
def get_pressure(request):
    """API endpoint for pressure reading"""
    return {"pressure": round(read_pressure(), 2)}

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

# Serve icon.png as the iOS home screen icon
@app.route('/icon.png')
def icon(request):
    with open('icon.png', 'rb') as f:
        icon = f.read()
    return Response(body=icon, headers={'Content-Type': 'image/png'})

# Catch-all: serve the captive portal page for all unknown URLs
@app.route('/<path:path>')
def catch_all(request, path):
    return captive_portal_page()

# Configuration for command execution
COMMAND_DURATION = 10  # seconds for a command to complete
last_command_time = {}  # Tracks when commands started (for backward compatibility)

# Adaptive pressure control parameters
PRESSURE_TOLERANCE = 0.5  # PSI tolerance for target pressure
ADJUSTMENT_INTERVAL = 1.0  # Seconds between adjustments
MIN_VALVE_TIME = 1.0     # Minimum valve open time (seconds)
MAX_VALVE_TIME_UP = 30.0  # Maximum valve open time for air_up (seconds)
MAX_VALVE_TIME_DOWN = 60.0  # Maximum valve open time for air_down (seconds)
LEARNING_RATE = 0.3      # How quickly to adapt (0-1)

async def adjust_pressure(cmd, target_psi):
    """Adaptive pressure adjustment function that learns system behavior"""
    print(f"Starting pressure adjustment: {cmd} to {target_psi} PSI")
    
    # Initialize learning parameters if they don't exist
    if 'observed_rate' not in command_state[cmd]:
        command_state[cmd]['observed_rate'] = None
    if 'last_pressure' not in command_state[cmd]:
        command_state[cmd]['last_pressure'] = await wait_for_stable_pressure()
    if 'last_valve_time' not in command_state[cmd]:
        command_state[cmd]['last_valve_time'] = 0.5  # Start conservative
    if 'last_action_time' not in command_state[cmd]:
        command_state[cmd]['last_action_time'] = time.time()
    
    # Flag to track if we're in learning mode or execution mode
    learning_mode = command_state[cmd]['observed_rate'] is None
    
    # Continue until cancelled or command_state is marked as not running
    while command_state[cmd]['running'] and not command_state[cmd]['cancel']:
        # Get stable pressure reading (important for accurate learning)
        print("Waiting for pressure to stabilize...")
        current_psi = await wait_for_stable_pressure(max_wait_time=3.0)
        pressure_diff = target_psi - current_psi
        current_time = time.time()
        
        # Check if we've reached or overshot the target
        if abs(pressure_diff) <= PRESSURE_TOLERANCE:
            # Within tolerance - perfect!
            print(f"Target reached: {current_psi:.1f} PSI")
            command_state[cmd]['running'] = False
            break
        elif (cmd == 'air_up' and current_psi > target_psi) or \
             (cmd == 'air_down' and current_psi < target_psi):
            # Overshot the target - just stop
            print(f"Target overshot: {current_psi:.1f} PSI (target was {target_psi:.1f})")
            command_state[cmd]['running'] = False
            break
            
        # Check if we should measure the rate of change
        time_since_last_action = current_time - command_state[cmd]['last_action_time']
        if time_since_last_action > 1.0 and command_state[cmd]['last_pressure'] > 0:
            # Calculate rate of change since last action
            pressure_change = current_psi - command_state[cmd]['last_pressure']
            rate = pressure_change / time_since_last_action  # PSI per second
            
            # If the pressure change is in the expected direction
            valid_change = (cmd == 'air_up' and pressure_change > 0) or \
                           (cmd == 'air_down' and pressure_change < 0)
            
            if valid_change and abs(rate) > 0.01:  # Ignore tiny changes
                # Update observed rate with smoothing
                rate = abs(rate)  # Use absolute value for calculations
                if command_state[cmd]['observed_rate'] is None:
                    command_state[cmd]['observed_rate'] = rate
                    print(f"Initial {cmd} rate: {rate:.3f} PSI/sec")
                else:
                    # Apply learning rate for smooth updates
                    command_state[cmd]['observed_rate'] = (
                        (1 - LEARNING_RATE) * command_state[cmd]['observed_rate'] + 
                        LEARNING_RATE * rate
                    )
                    print(f"Updated {cmd} rate: {command_state[cmd]['observed_rate']:.3f} PSI/sec")
        
        # Determine valve open time based on learning
        valve_time = 3.0  # Default conservative time
        
        # If we've observed a rate, calculate optimal valve time
        if command_state[cmd]['observed_rate'] is not None and abs(command_state[cmd]['observed_rate']) > 0.01:
            # Calculate how long to open valve to get close to target
            # Use 80% of calculated time as a safety factor
            valve_time = abs(pressure_diff) * 0.8 / command_state[cmd]['observed_rate']
            
            # Apply appropriate limits based on operation type
            if cmd == 'air_down':
                # Air down typically has lower flow rate
                valve_time = max(MIN_VALVE_TIME, min(MAX_VALVE_TIME_DOWN, valve_time))
            else:  # air_up
                # Air up typically has higher flow rate
                valve_time = max(MIN_VALVE_TIME, min(MAX_VALVE_TIME_UP, valve_time))
            
            # If very close to target, use minimum time
            if abs(pressure_diff) < 1.0:
                valve_time = MIN_VALVE_TIME
        
        # For air_up: activate fill valve if below target
        if cmd == 'air_up' and pressure_diff > 0:
            # Store current state for learning
            command_state[cmd]['last_pressure'] = current_psi
            command_state[cmd]['last_action_time'] = current_time
            command_state[cmd]['last_valve_time'] = valve_time
            
            print(f"Adjusting up: {current_psi:.1f} → {target_psi:.1f} PSI (valve: {valve_time:.2f}s)")
            compressed_air_relay.value(1)  # Open fill valve
            
            # Break valve operation into small chunks to check for cancel
            start_valve_time = time.time()
            while time.time() - start_valve_time < valve_time:
                # Check if operation was cancelled
                if command_state[cmd]['cancel']:
                    print(f"{cmd} cancelled during valve operation")
                    break
                # Sleep in small increments
                await asyncio.sleep(0.1)
                
            compressed_air_relay.value(0)  # Always close fill valve
            
            # If cancelled, exit the loop
            if command_state[cmd]['cancel']:
                command_state[cmd]['running'] = False
                break
        
        # For air_down: activate vent valve if above target
        elif cmd == 'air_down' and pressure_diff < 0:
            # Store current state for learning
            command_state[cmd]['last_pressure'] = current_psi
            command_state[cmd]['last_action_time'] = current_time
            command_state[cmd]['last_valve_time'] = valve_time
            
            print(f"Adjusting down: {current_psi:.1f} → {target_psi:.1f} PSI (valve: {valve_time:.2f}s)")
            vent_air_relay.value(1)  # Open vent valve
            
            # Break valve operation into small chunks to check for cancel
            start_valve_time = time.time()
            while time.time() - start_valve_time < valve_time:
                # Check if operation was cancelled
                if command_state[cmd]['cancel']:
                    print(f"{cmd} cancelled during valve operation")
                    break
                # Sleep in small increments
                await asyncio.sleep(0.1)
                
            vent_air_relay.value(0)  # Always close vent valve
            
            # If cancelled, exit the loop
            if command_state[cmd]['cancel']:
                command_state[cmd]['running'] = False
                break
        
        # No additional waiting needed - the wait_for_stable_pressure call
        # at the beginning of the loop already ensures adequate settling time

async def check_command_status():
    """Background task that monitors command state"""
    while True:
        current_time = time.time()
        
        # Check both commands
        for cmd in ['air_up', 'air_down']:
            # Check if command is running
            is_running = command_state[cmd]['running']
            
            # Safely access start_time
            start_time = 0
            if 'start_time' in command_state[cmd]:
                start_time = command_state[cmd]['start_time']
                
            has_start_time = cmd in last_command_time or start_time > 0
            
            if is_running and has_start_time:
                # Calculate elapsed time (for status reporting only)
                start_time = 0
                if 'start_time' in command_state[cmd]:
                    start_time = command_state[cmd]['start_time']
                    
                # Fall back to legacy timing if needed
                if start_time == 0 and cmd in last_command_time:
                    start_time = last_command_time[cmd]
                
                # Calculate elapsed time (for status API)
                elapsed = current_time - start_time
                # No logging here - removing periodic status updates

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

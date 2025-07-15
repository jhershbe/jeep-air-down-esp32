# Jeep Air Down Web Interface

Jeep Air Down is an ESP32-based project for automatically managing the tire pressure of an off-road vehicle. The ESP32 runs in access-point mode, creating its own WiFi network and serving a mobile-friendly web interface for real-time control and monitoring.

**How it works:**
- A pressure sensor measures the tire pressure through the fill hoses.
- One solenoid valve connects the tires to a compressed air source (for airing up).
- Another solenoid vents air from the tires (for airing down).
- The user connects the tires to the system, sets the desired pressures, and the system automatically adjusts each tire, freeing the user to focus on other tasks.

# Hardware Overview

This project uses the following hardware components:

- **ESP32 Development Board** ([Amazon link](https://www.amazon.com/dp/B0D5D7Q42V))
  - "ESP32 Development Board Max V1.0 Compatible with Arduino, USB-C, Wi-Fi, Bluetooth, MicroPython Compatible, Single Board Computer Suitable for Building Mini PC/Smart Robot/Game Console (QA009)"
- **Relay Shield** ([Amazon link](https://www.amazon.com/dp/B07F7Y55Z7))
  - "HiLetgo 5V 4 Channel Relay Shield for UNO R3"
- **Pneumatic Solenoid Valves** ([Amazon link](https://www.amazon.com/dp/B087T56KQN))
  - "1/4" NPT Brass Electric Solenoid Valve 12V DC Normally Closed VITON (Standard USA Pipe Thread). Solid Brass, Direct Acting, Viton Gasket Solenoid Valve by AOMAG"
- **Pressure Sensor** ([Amazon link](https://www.amazon.com/dp/B00NIK900K))
  - "200 Psi Pressure Transducer Sender Sensor with Connector Harness 1/8-27 NPT Thread Stainless Steel Fuel Pressure Sensors Compatible with Oil Fuel Air Water Diesel Gas"

**System Topology:**

- The ESP32 board runs the control software and hosts the WiFi web interface.
- The relay shield is connected to the ESP32 and controls the 12V pneumatic solenoid valves:
  - One relay/solenoid connects the tires to a compressed air source (for airing up).
  - Another relay/solenoid vents air from the tires (for airing down).
- The pressure sensor is plumbed into the air line to measure the current tire pressure and is connected to an analog input on the ESP32.
- The user connects all four tires to the system via hoses and can control the process from their phone or computer.

---

## Wiring Diagram

Below is a simplified wiring diagram showing the main connections between the ESP32, relay shield, solenoids, and pressure sensor:


```
         +--------------------------------+
         |   12V Power In (Barrel Jack)   |
         +--------------------------------+
                  |
                  |
        +---------------------+
        |   ESP32 Board       |
        |  (B0D5D7Q42V)       |
        +---------------------+
         |   |   |   |   |   |
         |   |   |   |   |   +-- GPIO5  <---+---[Button: Air Up]---+--- GND
         |   |   |   |   +------- GPIO16 <---+---[Button: Air Down]-+--- GND
         |   |   |   +----5V from ESP32  ---------+
         |   |   |                                |
         |   |   +-- GPIO32 (Analog0) <---+-------------------+
         |   |                            | Pressure Sensor   |
         |   +-- GPIO25 (Relay 4)         +-------------------+
         +------ GPIO14 (Relay 3)
         +---------- GPIO13 (Relay 2) --+-- NO2 on Relay Shield (Vent Solenoid) --+
         +---------- GPIO12 (Relay 1) --+-- NO1 on Relay Shield (Fill Solenoid) --+-- GND
         |
         +----------+-- Relay Shield V_in (jumpered to relay commons (COM1 & COM2))

Relay Shield NO1  --> Fill Solenoid (+)
Relay Shield NO2  --> Vent Solenoid (+)
Solenoid (-)      --> Relay Shield GND

Pressure Sensor V+     --> 5V on ESP32
Pressure Sensor GND    --> GND on ESP32
Pressure Sensor Signal --> GPIO32 (A0)

Air Up Button:   GPIO5  <---+---[Button]---+--- GND
Air Down Button: GPIO16 <---+---[Button]---+--- GND
```

**Description:**

- The ESP32 is powered by a 12V supply via the barrel jack, which also powers the relay shield and solenoids.
- The relay shield receives control signals from the ESP32 (GPIO12, 13, 14, 25), but only relays 1 and 2 are used for fill and vent solenoids.
- The relay shield's V_in is connected to 12V and jumpered to the common terminals of relays 1 and 2, allowing the NO (normally open) contacts to switch 12V to the solenoids.
- The solenoids' other wire is connected to relay shield GND.
- The pressure sensor is powered from the ESP32's 5V output, with its signal connected to analog input GPIO32 (A0).
- **Two pushbuttons are connected to the ESP32 for manual control:**
  - Air Up Button: Connect one side to GPIO5, the other to GND (active low, internal pull-up enabled)
  - Air Down Button: Connect one side to GPIO16, the other to GND (active low, internal pull-up enabled)
- The user connects the system to all four tires via hoses; the ESP32 web interface and/or physical buttons control the relays to air up or down as needed.

---

## Features
- ESP32 runs as a WiFi access point (default SSID: `JeepAirDown`, password: `emptyEveryPocket`)
- Real-time air pressure sensor readings via web interface
- Designed for easy use on iOS and Android devices
- Can be added to your phone's home screen as a web app

---

## Updating Default Setpoints

The default setpoints for "On Road" and "Off Road" are stored in `setpoints.json` in the project directory. To change the defaults:

1. Open `setpoints.json` in a text editor.
2. Change the values for `setpoint_onroad` and `setpoint_offroad` as desired (e.g., `{ "setpoint_onroad": 34, "setpoint_offroad": 16 }`).
3. Save the file.
4. Upload the updated `setpoints.json` to your ESP32 using Thonny (see below).

---

## Deployment Instructions (Using Thonny)

### 1. Prepare Your Files
- Download or clone this repository to your computer.
- Ensure you have the following files:
  - `main.py` (the main application)
  - `microdot.py` (from [Microdot GitHub repo](https://github.com/miguelgrinberg/microdot/tree/main/src))
  - `style.css` (for web app styling)
  - `setpoints.json` (default setpoints: On Road = 32 PSI, Off Road = 14 PSI)

### 2. Connect ESP32 to Your Computer
- Plug in your ESP32 via USB.
- Open Thonny IDE.
- Set the interpreter to "MicroPython (ESP32)" (bottom right corner).

### 3. Upload Files to ESP32
- In Thonny, use the left pane to browse to the project folder on your computer.
- Right-click `main.py` and `microdot.py`, then choose "Upload to /" to copy them to the ESP32.
- Confirm both files appear under "MicroPython device" in Thonny's file browser.

### 4. Reboot ESP32
- Press the reset button on the ESP32, or use "Stop/Restart backend" in Thonny.
- Watch the Thonny shell for output. You should see something like:
  ```
  AP active, IP: 192.168.4.1
  Starting Microdot server (blocking mode)...
  ```

### 5. Connect to the Web Interface
- On your phone, go to WiFi settings and connect to `JeepAirDown` (password: `emptyEveryPocket`).
- Open Safari or Chrome and visit: [http://192.168.4.1](http://192.168.4.1)
- The web interface should load and display the current pressure.

---

## Add to Home Screen (iOS/Android)

### iOS (iPhone/iPad)
1. Open Safari and navigate to [http://192.168.4.1](http://192.168.4.1)
2. Tap the Share button (square with arrow)
3. Scroll down and tap "Add to Home Screen"
4. Optionally, edit the name, then tap "Add"
5. The app icon will appear on your home screen for quick access

### Android
1. Open Chrome and go to [http://192.168.4.1](http://192.168.4.1)
2. Tap the menu (three dots)
3. Tap "Add to Home screen"
4. Follow prompts to add the shortcut

---

## Web App Meta Tags
The HTML page served by the ESP32 includes the following meta tags for a better mobile experience:
```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Jeep Air Down">
```
You can further customize the appearance by serving a custom icon as `/icon.png` (optional).

---

## Optimizing Performance with mpy-cross

### What is mpy-cross?
`mpy-cross` is a cross-compiler that converts MicroPython `.py` files into precompiled `.mpy` bytecode files. This has several advantages for ESP32 projects:

- **Reduced memory usage**: `.mpy` files consume less RAM when imported
- **Faster import times**: No need to compile code on the ESP32
- **More stable WiFi**: Less memory pressure helps maintain WiFi connectivity
- **Improved startup time**: The ESP32 boots faster with precompiled modules

### Installation

#### Option 1: Install via pip (Easiest)
```bash
# For any platform (Windows, macOS, Linux)
pip install mpy-cross

# Verify installation
mpy-cross --version
```

#### Option 2: Download binary

1. **Download mpy-cross**:
   - Visit the [MicroPython GitHub Releases page](https://github.com/micropython/micropython/releases)
   - Find the latest release that matches your MicroPython firmware version
   - Download the appropriate mpy-cross for your OS (Windows/Linux/Mac)

2. **Windows Installation**:
   ```
   # Extract the downloaded zip file
   # Add the mpy-cross directory to your PATH or use the full path
   ```

3. **Linux/Mac Installation**:
   ```bash
   chmod +x mpy-cross  # Make executable
   sudo mv mpy-cross /usr/local/bin/  # Move to path (optional)
   ```

### Compiling Libraries

```bash
# Basic usage
mpy-cross microdot.py

# For specific architecture (if needed)
mpy-cross -march=xtensawin microdot.py
```

This will create a `microdot.mpy` file that can be uploaded to the ESP32 instead of the `.py` version.

### Uploading Compiled Files

1. In Thonny, right-click the `.mpy` file and select "Upload to /"
2. Delete the corresponding `.py` file from the ESP32 if it exists
3. The ESP32 will now use the `.mpy` file automatically

### Recommended Libraries to Compile
- `microdot.py` → `microdot.mpy` (significant memory savings)
- Any other third-party libraries you're using

**Note**: Don't compile `main.py` or files you frequently modify during development.

---

## Troubleshooting
- If the web page does not load, ensure your phone is connected to the ESP32 WiFi and not using cellular data.
- If you see errors in Thonny, check that both `main.py` and either `microdot.py` or `microdot.mpy` are present on the ESP32.
- The captive portal may not automatically pop up on iOS; manually visit [http://192.168.4.1](http://192.168.4.1).
- If you experience WiFi connectivity issues, try using the `.mpy` compilation approach described above to reduce memory pressure.

---

## Credits
- Microdot by Miguel Grinberg: https://github.com/miguelgrinberg/microdot

---

For further help or to extend the project (e.g., adding valve control), open an issue or request additional features!

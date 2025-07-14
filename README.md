
# Jeep Air Down Web Interface

This project provides a simple web-based interface for controlling and monitoring an air pressure system using an ESP32 running MicroPython and Microdot. The ESP32 acts as a WiFi access point and serves a mobile-friendly web app for real-time pressure readings.

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

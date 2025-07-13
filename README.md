# ESP32 Air Pressure Web Interface

This project provides a simple web-based interface for controlling and monitoring an air pressure system using an ESP32 running MicroPython and Microdot. The ESP32 acts as a WiFi access point and serves a mobile-friendly web app for real-time pressure readings.

---

## Features
- ESP32 runs as a WiFi access point (default SSID: `ESP32-AirCtrl`, password: `esp32pass`)
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
- On your phone, go to WiFi settings and connect to `ESP32-AirCtrl` (password: `esp32pass`).
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
<meta name="apple-mobile-web-app-title" content="ESP32 AirCtrl">
```
You can further customize the appearance by serving a custom icon as `/icon.png` (optional).

---

## Troubleshooting
- If the web page does not load, ensure your phone is connected to the ESP32 WiFi and not using cellular data.
- If you see errors in Thonny, check that both `main.py` and `microdot.py` are present on the ESP32.
- The captive portal may not automatically pop up on iOS; manually visit [http://192.168.4.1](http://192.168.4.1).

---

## Credits
- Microdot by Miguel Grinberg: https://github.com/miguelgrinberg/microdot

---

For further help or to extend the project (e.g., adding valve control), open an issue or request additional features!

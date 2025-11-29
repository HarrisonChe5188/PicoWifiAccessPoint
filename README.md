# PicoWifiAccessPoint

A MicroPython script for the Raspberry Pi Pico 2 W that creates a WiFi access point. I've included a web interface for blinking morse code on the onboard LED while monitoring system statistics in real-time.

## Features

- **WiFi Access Point Mode**: Creates its own WiFi network that devices can connect to
- **Morse Code LED Blinker**: Convert text to morse code and blink it on the Pico W's onboard LED
- **Real-Time System Stats**: Monitor temperature and memory usage with auto-updating display
- **Single Page Interface**: All features accessible from one clean web interface
- **No Page Reloads**: AJAX-based updates keep you on the same page

## Hardware Requirements

- Raspberry Pi Pico W
- Micro=USB cable for power
- Any device with WiFi and a web browser (phone, laptop, tablet)
  - An aside, I couldn't figure out how to get it to work on my phone, but it worked fine on my laptop. I presume there may be blocks created by Apple to prevent connections to unsecure hosts.

## Installation

1. Install MicroPython on your Pico 2 W if you haven't already (I used Thonny as my IDE, but you can upload this code onto the pi directly.)
2. Copy the code to your Pico 2 W as `main.py`
3. If you wish, replace the current WiFi credentials in the code with your own:
   ```python
   ap_mode('Wi-Pi', '1234')
   ```
4. Save and reset your Pico W

## Usage

### Connecting to the Pico W

1. Power on your Pico W
2. Wait for the access point to activate (check the serial console for confirmation)
3. On your device, connect to the WiFi network you configured
4. Open a web browser and navigate to the IP address shown in the serial console (typically `192.168.4.1`)

### Morse Code Blinker

1. Enter text in the input field (letters, numbers, and spaces supported)
2. Click "Blink LED"
3. The onboard LED will blink your message in morse code
4. The morse code pattern will be displayed on the webpage

**Morse Code Timing:**
- Dot (`.`): 200ms blink
- Dash (`-`): 600ms blink (3x dot)
- Space between letters: 600ms pause
- Space between words: 1400ms pause

### System Statistics

The statistics panel automatically updates every 2 seconds showing:

- **Temperature**: Reading from the Pico W's onboard temperature sensor (°C)
- **Memory Usage**: Real-time memory allocation with visual progress bar
  - Allocated memory
  - Free memory
  - Total memory
  - Usage percentage

## API Endpoints

The web server provides three endpoints:

- `GET /` - Main web interface
- `GET /stats` - JSON endpoint for system statistics
- `GET /blink?text=YOUR_TEXT` - Trigger morse code LED blink

### Example JSON Response (`/stats`):
```json
{
  "temp": 23.5,
  "free_mem": 123456,
  "alloc_mem": 34567,
  "total_mem": 158023,
  "mem_percent": 21.9
}
```

## Code Structure

- **Morse Code Dictionary**: Complete International Morse Code alphabet (A-Z, 0-9)
- **LED Control**: Non-blocking LED blink using threading
- **Web Server**: Socket-based HTTP server on port 80
- **System Monitoring**: Real-time temperature and memory statistics
- **AJAX Updates**: Client-side JavaScript for seamless updates

## Troubleshooting

**Can't see the WiFi network:**
- Unplug your Pico W for 10 seconds and plug it back in
- Check the serial console for "AP Mode Is Active" message
- Verify the network name in your code matches what you're looking for

**Can't connect to the web interface:**
- Make sure you're connected to the Pico W's WiFi network
- Check the IP address in the serial console output
- Try `192.168.4.1` if no IP is shown

**LED not blinking:**
- Ensure your text only contains supported characters (A-Z, 0-9, spaces)
- Check that the LED isn't already blinking from a previous command
- Verify the onboard LED is working with a simple test

**Stats not updating:**
- Check your browser's JavaScript console for errors
- Try refreshing the page manually
- Ensure you have a stable connection to the Pico W

## Customization

### Adjust Morse Code Speed
Change the `dot_time` variable in the `blink_morse()` function:
```python
dot_time = 0.2  # Default 200ms, decrease for faster, increase for slower
```

### Change Stats Update Interval
Modify the interval in the JavaScript:
```javascript
setInterval(updateStats, 2000);  // Currently 2000ms (2 seconds)
```

### Modify WiFi Settings
Update the access point configuration:
```python
ap.config(essid=ssid, password=password)  # Add more parameters as needed
```

## Technical Details

- **Language**: MicroPython
- **Framework**: Raw sockets (no external web framework)
- **Port**: 80 (HTTP)
- **Threading**: Uses `_thread` module for non-blocking LED operations
- **Temperature Sensor**: ADC channel 4 (onboard sensor)
- **Memory Management**: Uses `gc` (garbage collector) module

## License

This project is open source and available for educational and personal use.

## Contributing

Feel free to fork, modify, and improve this code! Some ideas for enhancements:
- Add more LED patterns or animations
- Include WiFi signal strength monitoring
- Add uptime tracking
- Create a log of blinked messages
- Support for custom morse code timing profiles

## Credits

Built for the Raspberry Pi Pico 2 W microcontroller running MicroPython (I believe this will work on the Pico W as well).

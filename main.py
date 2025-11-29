import network
import time
import socket
import machine
import gc
import _thread

# LED setup
led = machine.Pin("LED", machine.Pin.OUT)

# Morse code dictionary
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', ' ': '/'
}

def text_to_morse(text):
    morse = []
    for char in text.upper():
        if char in MORSE_CODE:
            morse.append(MORSE_CODE[char])
    return ' '.join(morse)

def blink_morse(text):
    """Blink LED in morse code pattern"""
    morse = text_to_morse(text)
    dot_time = 0.2  # 200ms for a dot
    
    for char in morse:
        if char == '.':
            led.on()
            time.sleep(dot_time)
            led.off()
            time.sleep(dot_time)
        elif char == '-':
            led.on()
            time.sleep(dot_time * 3)  # Dash is 3x dot
            led.off()
            time.sleep(dot_time)
        elif char == ' ':
            time.sleep(dot_time * 3)  # Space between letters
        elif char == '/':
            time.sleep(dot_time * 7)  # Space between words

def get_system_stats():
    # Get memory stats
    gc.collect()
    free_mem = gc.mem_free()
    alloc_mem = gc.mem_alloc()
    total_mem = free_mem + alloc_mem
    
    # Get temperature from onboard sensor
    sensor_temp = machine.ADC(4)
    reading = sensor_temp.read_u16() * (3.3 / 65535)
    temperature = 27 - (reading - 0.706) / 0.001721
    
    return {
        'free_mem': free_mem,
        'alloc_mem': alloc_mem,
        'total_mem': total_mem,
        'temp': temperature
    }

def web_page(query_params):
    stats = get_system_stats()
    mem_percent = (stats['alloc_mem'] / stats['total_mem']) * 100
    
    html = f"""<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial; margin: 20px; background: #f0f0f0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; font-size: 24px; margin-bottom: 10px; }}
        h2 {{ color: #555; font-size: 20px; margin-top: 30px; border-top: 2px solid #eee; padding-top: 20px; }}
        input[type="text"] {{ width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; border: 2px solid #ddd; border-radius: 5px; }}
        button {{ background: #4CAF50; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background: #45a049; }}
        .morse-output {{ background: #e8f5e9; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; font-family: monospace; font-size: 16px; }}
        .stat-box {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }}
        .stat-label {{ font-weight: bold; color: #555; font-size: 14px; }}
        .stat-value {{ font-size: 28px; color: #2196F3; margin: 5px 0; }}
        .progress-bar {{ background: #ddd; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }}
        .progress-fill {{ background: #2196F3; height: 100%; transition: width 0.3s; }}
        .info {{ font-size: 12px; color: #666; margin-top: 5px; }}
    </style>
    <script>
        async function updateStats() {{
            try {{
                const response = await fetch('/stats');
                const data = await response.json();
                
                document.getElementById('temp-value').textContent = data.temp.toFixed(1) + '°C';
                document.getElementById('mem-progress').style.width = data.mem_percent.toFixed(1) + '%';
                document.getElementById('mem-info').innerHTML = 
                    'Allocated: ' + data.alloc_mem + ' bytes (' + data.mem_percent.toFixed(1) + '%)<br>' +
                    'Free: ' + data.free_mem + ' bytes<br>' +
                    'Total: ' + data.total_mem + ' bytes';
            }} catch(e) {{
                console.error('Failed to update stats:', e);
            }}
        }}
        
        async function blinkMorse() {{
            const text = document.getElementById('morse-input').value;
            if (!text) return;
            
            try {{
                const response = await fetch('/blink?text=' + encodeURIComponent(text));
                const data = await response.json();
                document.getElementById('morse-status').innerHTML = 
                    '<div class="morse-output">LED is blinking: ' + data.morse + '</div>';
            }} catch(e) {{
                console.error('Failed to blink morse:', e);
            }}
        }}
        
        // Update stats every 2 seconds
        setInterval(updateStats, 2000);
        updateStats(); // Initial update
    </script>
</head>
<body>
    <div class="container">
        <h1>Pico W Control Panel</h1>
        
        <h2>Morse Code LED Blinker</h2>
        <input type="text" id="morse-input" placeholder="Enter text to blink on LED..." />
        <button onclick="blinkMorse()">Blink LED</button>
        <div id="morse-status"></div>
        
        <h2>System Statistics</h2>
        
        <div class="stat-box">
            <div class="stat-label">Temperature</div>
            <div class="stat-value" id="temp-value">{stats['temp']:.1f}°C</div>
        </div>
        
        <div class="stat-box">
            <div class="stat-label">Memory Usage</div>
            <div class="progress-bar">
                <div class="progress-fill" id="mem-progress" style="width: {mem_percent:.1f}%"></div>
            </div>
            <div class="info" id="mem-info">
                Allocated: {stats['alloc_mem']} bytes ({mem_percent:.1f}%)<br>
                Free: {stats['free_mem']} bytes<br>
                Total: {stats['total_mem']} bytes
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html

def parse_request(request):
    try:
        request_str = request.decode('utf-8')
        lines = request_str.split('\r\n')
        first_line = lines[0].split(' ')
        method = first_line[0]
        full_path = first_line[1]
        
        # Parse path and query string
        if '?' in full_path:
            path, query_string = full_path.split('?', 1)
            query_params = {}
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    # URL decode
                    value = value.replace('+', ' ')
                    query_params[key] = value
        else:
            path = full_path
            query_params = {}
        
        return path, query_params
    except:
        return '/', {}

def ap_mode(ssid, password):
    """
        Description: This is a function to activate AP mode

        Parameters:

        ssid[str]: The name of your internet connection
        password[str]: Password for your internet connection

        Returns: Nada
    """
    # Just making our internet connection
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while ap.active() == False:
        pass
    print('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        print('Content = %s' % str(request))
        
        path, query_params = parse_request(request)
        
        # Handle different routes
        if path == '/stats':
            # Return JSON for stats endpoint
            stats = get_system_stats()
            mem_percent = (stats['alloc_mem'] / stats['total_mem']) * 100
            response = '{"temp": %.1f, "free_mem": %d, "alloc_mem": %d, "total_mem": %d, "mem_percent": %.1f}' % (
                stats['temp'], stats['free_mem'], stats['alloc_mem'], stats['total_mem'], mem_percent
            )
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
        elif path == '/blink':
            # Handle morse code blink request
            text = query_params.get('text', '')
            if text:
                morse = text_to_morse(text)
                # Blink LED in separate thread
                _thread.start_new_thread(blink_morse, (text,))
                response = '{"morse": "%s"}' % morse
            else:
                response = '{"morse": ""}'
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
        else:
            # Return HTML for main page
            response = web_page(query_params)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
        
        conn.close()

ap_mode('Wi-Pi', '1234')

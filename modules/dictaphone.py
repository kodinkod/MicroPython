import network
import urequests
import time
import gc
from recorder import Recorder

SERVER_URL = "http://YOUR_SERVER:5000/transcribe"
WIFI_SSID = "MTS_GPON_2197"
WIFI_PASS = "8xjuyZrQyx"

class Dictaphone:
    def __init__(self, server_url=None):
        self.server_url = server_url or SERVER_URL
        self.recorder = None
        self.wlan = None

    def connect_wifi(self, ssid=None, password=None):
        ssid = ssid or WIFI_SSID
        password = password or WIFI_PASS

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        if self.wlan.isconnected():
            print(f"Already connected: {self.wlan.ifconfig()[0]}")
            return True

        print(f"Connecting to {ssid}...")
        self.wlan.connect(ssid, password)

        for _ in range(20):
            if self.wlan.isconnected():
                print(f"Connected! IP: {self.wlan.ifconfig()[0]}")
                return True
            time.sleep(0.5)

        print("WiFi connection failed")
        return False

    def init_recorder(self, sample_rate=16000):
        self.recorder = Recorder(sample_rate=sample_rate, bits=16)
        self.recorder.init()
        print("Recorder ready")

    def record_to_file(self, filename, duration_ms=5000):
        if not self.recorder:
            self.init_recorder()

        print(f"🎤 Recording {duration_ms}ms → {filename}")
        self.recorder.record_to_file(filename, duration_ms)
        print(f"✅ Recorded to {filename}")
        return filename

    def send_file(self, filename):
        if not self.wlan or not self.wlan.isconnected():
            print("📶 Not connected to WiFi")
            return None

        print(f"📤 Sending {filename}...")

        try:
            with open(filename, 'rb') as f:
                headers = {'Content-Type': 'audio/wav'}
                response = urequests.post(self.server_url, data=f, headers=headers)

            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('text', 'No text')}")
                response.close()
                return result
            else:
                print(f"❌ Server: {response.status_code}")
                response.close()
                return None

        except Exception as e:
            print(f"❌ Send error: {e}")
            return None

    def record_and_transcribe(self, duration_ms=5000, temp_filename="temp_audio.wav"):
        filename = self.record_to_file(temp_filename, duration_ms)
        result = self.send_file(filename)
        
        return result.get('text') if result else None

    def run_interactive(self):
        print("\n=== Smart Dictaphone ===")
        print("Enter → 5s | r 10 → 10s | q → quit")

        while True:
            cmd = input("> ").strip().lower()

            if cmd == 'q':
                break
            elif cmd.startswith('r '):
                try:
                    seconds = int(cmd.split()[1])
                    self.record_and_transcribe(seconds * 1000)
                except:
                    print("r <seconds>")
            else:
                self.record_and_transcribe(5000)

        if self.recorder:
            self.recorder.deinit()
        print("Goodbye!")

def start(ssid=None, password=None, server=None):
    d = Dictaphone(server)
    if ssid:
        d.connect_wifi(ssid, password)
    d.init_recorder()
    return d

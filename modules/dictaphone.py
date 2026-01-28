import network
import urequests
import time
import gc
from recorder import Recorder

SERVER_URL = "http://192.168.1.45:5001/transcribe"
WIFI_SSID = "MTS_GPON_2197"
WIFI_PASS = "8xjuyZrQyx"

def to_translit(text):
    translit = {
        'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'е':'e', 'ё':'yo',
        'ж':'zh', 'з':'z', 'и':'i', 'й':'y', 'к':'k', 'л':'l', 'м':'m',
        'н':'n', 'о':'o', 'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u',
        'ф':'f', 'х':'h', 'ц':'c', 'ч':'ch', 'ш':'sh', 'щ':'sch',
        'ъ':'', 'ы':'y', 'ь':'', 'э':'e', 'ю':'yu', 'я':'ya'
    }
    return ''.join(translit.get(c.lower(), c) for c in text)

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

        print(f"-rec-", end="")
        self.recorder.record_to_file(filename, duration_ms)
        print("-done-", end="")
        return filename

    def send_file(self, filename):
        if not self.wlan or not self.wlan.isconnected():
            print("Not connected to WiFi")
            return None

        print("-sending-", end="")
        try:
            with open(filename, 'rb') as f:
                headers = {'Content-Type': 'audio/wav'}
                response = urequests.post(self.server_url, data=f, headers=headers)

            if response.status_code == 200:
                result = response.json()
                response.close()
                return result
            else:
                response.close()
                return None

        except Exception as e:
            print(f"Send error: {e}")
            return None

    def record_and_transcribe(self, duration_ms=5000, temp_filename="temp_audio.wav"):
        filename = self.record_to_file(temp_filename, duration_ms)
        result = self.send_file(filename)
        text = result.get('text', 'No text').encode('utf-8').decode('utf-8')
        return text

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
                    res = self.record_and_transcribe(seconds * 1000)
                    print(to_translit(res))
                except:
                    print("r <seconds>")
            else:
                res = self.record_and_transcribe(5000)
                print(to_translit(res))

        if self.recorder:
            self.recorder.deinit()
        print("Goodbye!")

def start():
    d = Dictaphone(SERVER_URL)
    d.connect_wifi(WIFI_SSID, WIFI_PASS)
    d.init_recorder()
    return d

d = start()
d.run_interactive()
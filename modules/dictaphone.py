# Smart Dictaphone for M5Stack Cardputer ADV
# Records audio and sends to server for transcription

import network
import urequests
import time
import gc
from recorder import Recorder

# Server configuration
SERVER_URL = "http://YOUR_SERVER:5000/transcribe"

# WiFi configuration
WIFI_SSID = "MTS_GPON_2197"
WIFI_PASS = "8xjuyZrQyx"


class Dictaphone:
    def __init__(self, server_url=None):
        self.server_url = server_url or SERVER_URL
        self.recorder = None
        self.wlan = None

    def connect_wifi(self, ssid=None, password=None):
        """Connect to WiFi"""
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
        """Initialize audio recorder"""
        self.recorder = Recorder(sample_rate=sample_rate, bits=16)
        self.recorder.init()
        print("Recorder ready")

    def record(self, duration_ms=3000):
        """Record audio and return as bytes (max ~3 sec due to RAM)"""
        if not self.recorder:
            self.init_recorder()

        # Limit duration to avoid MemoryError (ESP32 has ~200KB free)
        max_duration = 3000  # 3 sec = ~96KB
        if duration_ms > max_duration:
            print(f"Warning: limiting to {max_duration}ms due to RAM")
            duration_ms = max_duration

        print(f"Recording {duration_ms}ms...")
        audio_data = self.recorder.record_to_buffer(duration_ms)
        print(f"Recorded {len(audio_data)} bytes")

        return audio_data

    def record_to_file(self, filename, duration_ms=5000):
        """Record audio to WAV file"""
        if not self.recorder:
            self.init_recorder()

        self.recorder.record_to_file(filename, duration_ms)
        return filename

    def send_audio(self, audio_data):
        """Send audio to server for transcription"""
        if not self.wlan or not self.wlan.isconnected():
            print("Not connected to WiFi")
            return None

        print(f"Sending {len(audio_data)} bytes to server...")
        gc.collect()

        try:
            # Create minimal WAV header (44 bytes)
            header = self._create_wav_header(len(audio_data))

            # Send header + data
            headers = {'Content-Type': 'audio/wav'}
            # Combine header and data
            wav_data = header + audio_data

            response = urequests.post(
                self.server_url,
                data=wav_data,
                headers=headers
            )

            result = None
            if response.status_code == 200:
                result = response.json()
            else:
                print(f"Server error: {response.status_code}")
                print(response.text)

            response.close()
            del wav_data
            gc.collect()
            return result

        except Exception as e:
            print(f"Error sending audio: {e}")
            gc.collect()
            return None

    def _create_wav_header(self, data_size):
        """Create WAV header (44 bytes)"""
        import struct

        sample_rate = self.recorder.sample_rate if self.recorder else 16000
        bits = 16
        num_channels = 1
        byte_rate = sample_rate * num_channels * (bits // 8)
        block_align = num_channels * (bits // 8)

        header = bytearray(44)

        # RIFF header
        header[0:4] = b'RIFF'
        struct.pack_into('<I', header, 4, 36 + data_size)
        header[8:12] = b'WAVE'

        # fmt chunk
        header[12:16] = b'fmt '
        struct.pack_into('<I', header, 16, 16)
        struct.pack_into('<H', header, 20, 1)
        struct.pack_into('<H', header, 22, num_channels)
        struct.pack_into('<I', header, 24, sample_rate)
        struct.pack_into('<I', header, 28, byte_rate)
        struct.pack_into('<H', header, 32, block_align)
        struct.pack_into('<H', header, 34, bits)

        # data chunk
        header[36:40] = b'data'
        struct.pack_into('<I', header, 40, data_size)

        return bytes(header)

    def record_and_transcribe(self, duration_ms=5000):
        """Record audio and send for transcription"""
        audio = self.record(duration_ms)
        result = self.send_audio(audio)

        if result and 'text' in result:
            print(f"Transcription: {result['text']}")
            return result['text']

        return None

    def run_interactive(self):
        """Interactive mode - press Enter to record"""
        print("\n=== Smart Dictaphone ===")
        print("Press Enter to record 5 seconds")
        print("Type 'q' to quit\n")

        while True:
            cmd = input("> ").strip().lower()

            if cmd == 'q' or cmd == 'quit':
                break
            elif cmd.startswith('r '):
                # Custom duration: r 10 (10 seconds)
                try:
                    seconds = int(cmd.split()[1])
                    self.record_and_transcribe(seconds * 1000)
                except:
                    print("Usage: r <seconds>")
            else:
                self.record_and_transcribe(5000)

        if self.recorder:
            self.recorder.deinit()
        print("Goodbye!")


# Quick start functions
def start(ssid=None, password=None, server=None):
    """Quick start dictaphone"""
    d = Dictaphone(server)

    if ssid:
        d.connect_wifi(ssid, password)

    d.init_recorder()
    return d


def demo():
    """Demo: record and save to file"""
    d = Dictaphone()
    d.init_recorder()
    d.record_to_file("demo.wav", 3000)
    d.recorder.deinit()
    print("Saved to demo.wav")

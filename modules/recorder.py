# Audio Recorder for M5Stack Cardputer ADV
# Uses ES8311 codec and I2S

from machine import I2S, Pin
import es8311

# I2S configuration for Cardputer ADV
I2S_ID = 0
I2S_BCK = 41
I2S_WS = 43
I2S_DIN = 46  # Microphone input


class Recorder:
    def __init__(self, sample_rate=16000, bits=16, buffer_size=4096):
        """
        Initialize audio recorder
        sample_rate: 8000, 16000, 22050, 44100 Hz
        bits: 16 or 32
        buffer_size: I2S buffer size in bytes
        """
        self.sample_rate = sample_rate
        self.bits = bits
        self.buffer_size = buffer_size
        self.codec = None
        self.i2s = None
        self._is_recording = False

    def init(self):
        """Initialize codec and I2S"""
        # Initialize ES8311 codec
        self.codec = es8311.init_cardputer_audio()
        if self.codec is None:
            raise RuntimeError("Failed to initialize ES8311 codec")

        # Initialize I2S for microphone input
        self.i2s = I2S(
            I2S_ID,
            sck=Pin(I2S_BCK),
            ws=Pin(I2S_WS),
            sd=Pin(I2S_DIN),
            mode=I2S.RX,
            bits=self.bits,
            format=I2S.MONO,
            rate=self.sample_rate,
            ibuf=self.buffer_size
        )
        print(f"I2S initialized: {self.sample_rate}Hz, {self.bits}-bit, buf={self.buffer_size}")

    def deinit(self):
        """Deinitialize I2S"""
        if self.i2s:
            self.i2s.deinit()
            self.i2s = None

    def read(self, num_bytes):
        """Read raw audio data from microphone"""
        if not self.i2s:
            raise RuntimeError("Recorder not initialized")
        buf = bytearray(num_bytes)
        self.i2s.readinto(buf)
        return buf

    def record_to_buffer(self, duration_ms):
        """
        Record audio for specified duration
        Returns bytearray with raw PCM data
        """
        if not self.i2s:
            raise RuntimeError("Recorder not initialized")

        bytes_per_sample = self.bits // 8
        total_samples = (self.sample_rate * duration_ms) // 1000
        total_bytes = total_samples * bytes_per_sample

        audio_data = bytearray(total_bytes)
        bytes_read = 0

        chunk_size = min(1024, total_bytes)
        chunk = bytearray(chunk_size)

        while bytes_read < total_bytes:
            to_read = min(chunk_size, total_bytes - bytes_read)
            n = self.i2s.readinto(chunk)
            if n > 0:
                audio_data[bytes_read:bytes_read + n] = chunk[:n]
                bytes_read += n

        return audio_data

    def record_to_file(self, filename, duration_ms):
        """
        Record audio directly to file (WAV format)
        """
        if not self.i2s:
            raise RuntimeError("Recorder not initialized")

        bytes_per_sample = self.bits // 8
        total_samples = (self.sample_rate * duration_ms) // 1000
        total_bytes = total_samples * bytes_per_sample

        # Write WAV file
        with open(filename, 'wb') as f:
            # Write WAV header
            self._write_wav_header(f, total_bytes)

            # Record audio
            chunk_size = 1024
            chunk = bytearray(chunk_size)
            bytes_written = 0

            print(f"Recording {duration_ms}ms to {filename}...")
            while bytes_written < total_bytes:
                n = self.i2s.readinto(chunk)
                if n > 0:
                    to_write = min(n, total_bytes - bytes_written)
                    f.write(chunk[:to_write])
                    bytes_written += to_write

        print(f"Recorded {bytes_written} bytes")
        return bytes_written

    def _write_wav_header(self, f, data_size):
        """Write WAV file header"""
        import struct

        num_channels = 1
        byte_rate = self.sample_rate * num_channels * (self.bits // 8)
        block_align = num_channels * (self.bits // 8)

        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))  # File size - 8
        f.write(b'WAVE')

        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # Chunk size
        f.write(struct.pack('<H', 1))   # Audio format (PCM)
        f.write(struct.pack('<H', num_channels))
        f.write(struct.pack('<I', self.sample_rate))
        f.write(struct.pack('<I', byte_rate))
        f.write(struct.pack('<H', block_align))
        f.write(struct.pack('<H', self.bits))

        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', data_size))

    def set_mic_gain(self, gain_db):
        """Set microphone gain (0-24 dB)"""
        if self.codec:
            self.codec.set_mic_gain(gain_db)


# Quick test function
def test_record():
    """Test recording - records 3 seconds"""
    rec = Recorder(sample_rate=16000, bits=16)
    rec.init()

    print("Recording 3 seconds...")
    rec.record_to_file("test.wav", 3000)

    rec.deinit()
    print("Done! File saved as test.wav")


def test_levels():
    """Test microphone levels"""
    rec = Recorder(sample_rate=16000, bits=16)
    rec.init()

    import struct
    print("Monitoring mic levels (Ctrl+C to stop)...")

    try:
        while True:
            data = rec.read(512)
            # Calculate RMS level
            samples = struct.unpack('<' + 'h' * (len(data) // 2), data)
            rms = sum(s * s for s in samples) / len(samples)
            rms = int(rms ** 0.5)
            # Simple bar display
            bar = '#' * min(40, rms // 100)
            print(f"\r{rms:5d} |{bar:<40}|", end='')
    except KeyboardInterrupt:
        pass

    rec.deinit()
    print("\nDone")

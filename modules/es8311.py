# ES8311 Audio Codec Driver for MicroPython
# For M5Stack Cardputer ADV
# Based on Espressif ESP-ADF driver

from machine import I2C, Pin

# ES8311 I2C Address
ES8311_ADDR = 0x18

# ES8311 Register Addresses
ES8311_REG00_RESET = 0x00
ES8311_REG01_CLK_MANAGER = 0x01
ES8311_REG02_CLK_MANAGER = 0x02
ES8311_REG03_CLK_MANAGER = 0x03
ES8311_REG04_CLK_MANAGER = 0x04
ES8311_REG05_CLK_MANAGER = 0x05
ES8311_REG06_CLK_MANAGER = 0x06
ES8311_REG07_CLK_MANAGER = 0x07
ES8311_REG08_CLK_MANAGER = 0x08
ES8311_REG09_SDP_IN = 0x09
ES8311_REG0A_SDP_OUT = 0x0A
ES8311_REG0B_SYSTEM = 0x0B
ES8311_REG0C_SYSTEM = 0x0C
ES8311_REG0D_SYSTEM = 0x0D
ES8311_REG0E_SYSTEM = 0x0E
ES8311_REG0F_SYSTEM = 0x0F
ES8311_REG10_SYSTEM = 0x10
ES8311_REG11_SYSTEM = 0x11
ES8311_REG12_SYSTEM = 0x12
ES8311_REG13_SYSTEM = 0x13
ES8311_REG14_ADC = 0x14
ES8311_REG15_ADC = 0x15
ES8311_REG16_ADC = 0x16
ES8311_REG17_ADC = 0x17
ES8311_REG18_ADC = 0x18
ES8311_REG19_ADC = 0x19
ES8311_REG1A_ADC = 0x1A
ES8311_REG1B_ADC = 0x1B
ES8311_REG1C_ADC = 0x1C
ES8311_REG32_DAC = 0x32
ES8311_REG37_DAC = 0x37
ES8311_REG44_GPIO = 0x44
ES8311_REG45_GPIO = 0x45
ES8311_REGFA_ID = 0xFA
ES8311_REGFB_ID = 0xFB
ES8311_REGFC_ID = 0xFC
ES8311_REGFD_CHIPVER = 0xFD


class ES8311:
    def __init__(self, i2c, addr=ES8311_ADDR):
        self.i2c = i2c
        self.addr = addr
        self._buf = bytearray(1)

    def _write_reg(self, reg, val):
        self._buf[0] = val
        self.i2c.writeto_mem(self.addr, reg, self._buf)

    def _read_reg(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _update_reg(self, reg, mask, val):
        old = self._read_reg(reg)
        new = (old & ~mask) | (val & mask)
        self._write_reg(reg, new)

    def get_chip_id(self):
        """Get ES8311 chip ID (should return 0x83, 0x11)"""
        id1 = self._read_reg(ES8311_REGFD_CHIPVER)
        return id1

    def reset(self):
        """Software reset"""
        self._write_reg(ES8311_REG00_RESET, 0x1F)
        self._write_reg(ES8311_REG00_RESET, 0x00)

    def init(self, sample_rate=16000, bits=16):
        """
        Initialize ES8311 for recording (from ESP-ADF driver)
        sample_rate: 8000, 16000, 22050, 32000, 44100, 48000
        bits: 16, 24, 32
        """
        # Step 1: I2C noise immunity (write twice per ESP-ADF)
        self._write_reg(ES8311_REG44_GPIO, 0x08)
        self._write_reg(ES8311_REG44_GPIO, 0x08)

        # Step 2: Clock manager init
        self._write_reg(ES8311_REG01_CLK_MANAGER, 0x30)  # MCLK from BCLK
        self._write_reg(ES8311_REG02_CLK_MANAGER, 0x00)  # Clock divider
        self._write_reg(ES8311_REG03_CLK_MANAGER, 0x10)  # ADC OSR
        self._write_reg(ES8311_REG16_ADC, 0x24)          # ADC gain scale
        self._write_reg(ES8311_REG04_CLK_MANAGER, 0x10)  # DAC OSR
        self._write_reg(ES8311_REG05_CLK_MANAGER, 0x00)  # ADC/DAC divider

        # Step 3: I2S format
        if bits == 16:
            self._write_reg(ES8311_REG09_SDP_IN, 0x0C)   # I2S 16-bit
            self._write_reg(ES8311_REG0A_SDP_OUT, 0x0C)  # I2S 16-bit
        elif bits == 24:
            self._write_reg(ES8311_REG09_SDP_IN, 0x00)
            self._write_reg(ES8311_REG0A_SDP_OUT, 0x00)
        else:  # 32-bit
            self._write_reg(ES8311_REG09_SDP_IN, 0x04)
            self._write_reg(ES8311_REG0A_SDP_OUT, 0x04)

        # Step 4: System registers
        self._write_reg(ES8311_REG0B_SYSTEM, 0x00)
        self._write_reg(ES8311_REG0C_SYSTEM, 0x00)
        self._write_reg(ES8311_REG10_SYSTEM, 0x1F)
        self._write_reg(ES8311_REG11_SYSTEM, 0x7F)

        # Step 5: Reset register - enable CSM
        self._write_reg(ES8311_REG00_RESET, 0x80)

        # Step 6: More clock config
        self._write_reg(ES8311_REG01_CLK_MANAGER, 0x3F)  # Enable all clocks
        self._write_reg(ES8311_REG13_SYSTEM, 0x10)

        # Step 7: ADC gain/volume
        self._write_reg(ES8311_REG1B_ADC, 0x0A)
        self._write_reg(ES8311_REG1C_ADC, 0x6A)

        # Step 8: Start ADC (ES_MODULE_ADC sequence from ESP-ADF)
        self._write_reg(ES8311_REG17_ADC, 0xBF)         # ADC unmute, volume
        self._write_reg(ES8311_REG0E_SYSTEM, 0x02)      # Enable ADC
        self._write_reg(ES8311_REG12_SYSTEM, 0x00)
        self._write_reg(ES8311_REG14_ADC, 0x1A)         # PGA gain +30dB
        self._write_reg(ES8311_REG0D_SYSTEM, 0x01)      # Power up analog
        self._write_reg(ES8311_REG15_ADC, 0x40)         # ADC config
        self._write_reg(ES8311_REG44_GPIO, 0x58)        # GPIO config for ADC

    def set_mic_gain(self, gain_db):
        """Set microphone gain (0-24 dB in 3dB steps)"""
        gain = min(8, max(0, gain_db // 3))
        self._write_reg(ES8311_REG14_ADC, gain)

    def set_adc_volume(self, volume):
        """Set ADC volume (0-255)"""
        self._write_reg(ES8311_REG17_ADC, volume)

    def mute_adc(self, mute=True):
        """Mute/unmute ADC"""
        if mute:
            self._update_reg(ES8311_REG17_ADC, 0x80, 0x80)
        else:
            self._update_reg(ES8311_REG17_ADC, 0x80, 0x00)

    def enable_speaker(self):
        """Enable DAC/speaker output"""
        self._write_reg(ES8311_REG32_DAC, 0x00)
        self._write_reg(ES8311_REG37_DAC, 0x08)

    def disable_speaker(self):
        """Disable DAC/speaker output"""
        self._write_reg(ES8311_REG32_DAC, 0x00)
        self._write_reg(ES8311_REG37_DAC, 0x00)

    def set_dac_volume(self, volume):
        """Set DAC volume (0-255)"""
        self._write_reg(ES8311_REG32_DAC, volume)


# Cardputer ADV specific pins
CARDPUTER_I2S_BCK = 41
CARDPUTER_I2S_WS = 43
CARDPUTER_I2S_DIN = 46   # Microphone data
CARDPUTER_I2S_DOUT = 42  # Speaker data
CARDPUTER_I2C_SDA = 8
CARDPUTER_I2C_SCL = 9


def init_cardputer_audio():
    """Initialize ES8311 on Cardputer ADV"""
    from machine import SoftI2C

    i2c = SoftI2C(scl=Pin(CARDPUTER_I2C_SCL), sda=Pin(CARDPUTER_I2C_SDA), freq=100000)

    # Check if ES8311 is present
    devices = i2c.scan()
    if ES8311_ADDR not in devices:
        print("ES8311 not found! Found devices:", [hex(d) for d in devices])
        return None

    codec = ES8311(i2c)
    chip_id = codec.get_chip_id()
    print(f"ES8311 found, chip version: {hex(chip_id)}")

    codec.init(sample_rate=16000, bits=16)
    print("ES8311 initialized for 16kHz 16-bit recording (ESP-ADF sequence)")

    return codec

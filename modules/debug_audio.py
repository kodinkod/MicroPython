# Debug Audio for M5Stack Cardputer ADV
# Диагностика ES8311 и I2S микрофона

from machine import SoftI2C, Pin, I2S

# Пины Cardputer ADV
I2C_SDA = 8
I2C_SCL = 9
I2S_BCK = 41
I2S_WS = 43
I2S_DIN = 46

i2c = None


def init_i2c():
    """Инициализация I2C"""
    global i2c
    i2c = SoftI2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=100000)
    print(f"I2C init: SDA={I2C_SDA}, SCL={I2C_SCL}")
    return i2c


def scan():
    """Сканирование I2C устройств"""
    if not i2c:
        init_i2c()
    devices = i2c.scan()
    print("I2C devices found:")
    for d in devices:
        name = ""
        if d == 0x18:
            name = " (ES8311)"
        elif d == 0x34:
            name = " (TCA8418 keyboard)"
        elif d == 0x69:
            name = " (BMI270 IMU)"
        print(f"  0x{d:02X} ({d}){name}")
    return devices


def wr(reg, val):
    """Запись регистра ES8311"""
    if not i2c:
        init_i2c()
    i2c.writeto_mem(0x18, reg, bytes([val]))


def rd(reg):
    """Чтение регистра ES8311"""
    if not i2c:
        init_i2c()
    return i2c.readfrom_mem(0x18, reg, 1)[0]


def dump_regs():
    """Вывод всех важных регистров ES8311"""
    if not i2c:
        init_i2c()

    regs = {
        0x00: "RESET",
        0x01: "CLK_MGR1",
        0x02: "CLK_MGR2",
        0x03: "CLK_MGR3",
        0x04: "CLK_MGR4",
        0x05: "CLK_MGR5",
        0x06: "CLK_MGR6",
        0x07: "CLK_MGR7",
        0x08: "CLK_MGR8",
        0x09: "SDP_IN",
        0x0A: "SDP_OUT",
        0x0B: "SYS1",
        0x0C: "SYS2",
        0x0D: "SYS3",
        0x0E: "SYS4",
        0x0F: "SYS5",
        0x10: "SYS6",
        0x11: "SYS7",
        0x12: "SYS8",
        0x13: "SYS9",
        0x14: "ADC1",
        0x15: "ADC2",
        0x16: "ADC3",
        0x17: "ADC4_VOL",
        0x1B: "ADC5",
        0x1C: "ADC6",
        0x32: "DAC_VOL",
        0x37: "DAC2",
        0x44: "GPIO",
        0x45: "GPIO2",
        0xFD: "CHIP_VER",
    }

    print("\n=== ES8311 Registers ===")
    for reg, name in regs.items():
        val = rd(reg)
        print(f"0x{reg:02X} {name:10s} = 0x{val:02X} ({val:3d}) {bin(val)}")
    print()


def init_es8311_adc():
    """Полная инициализация ES8311 для записи с микрофона"""
    if not i2c:
        init_i2c()

    print("Initializing ES8311 for ADC/microphone...")

    # Reset
    wr(0x00, 0x1F)
    wr(0x00, 0x00)

    # I2C noise immunity (write twice)
    wr(0x44, 0x08)
    wr(0x44, 0x08)

    # Clock manager - MCLK from BCLK
    wr(0x01, 0x3F)  # Enable all clocks
    wr(0x02, 0x00)  # Prediv
    wr(0x03, 0x10)  # ADC OSR
    wr(0x04, 0x10)  # DAC OSR
    wr(0x05, 0x00)  # CLK div
    wr(0x06, 0x03)  # BCLK div
    wr(0x07, 0x00)  # Tri-state
    wr(0x08, 0xFF)  # CLK on

    # I2S format - 16-bit
    wr(0x09, 0x0C)
    wr(0x0A, 0x0C)

    # System registers
    wr(0x0B, 0x00)
    wr(0x0C, 0x00)
    wr(0x10, 0x1F)
    wr(0x11, 0x7F)

    # Power up digital
    wr(0x00, 0x80)

    # ADC power and config
    wr(0x0D, 0x01)  # Analog power up
    wr(0x0E, 0x02)  # ADC power up
    wr(0x0F, 0x00)  # ADC reference
    wr(0x12, 0x00)
    wr(0x13, 0x10)

    # ADC gain and volume - MAX
    wr(0x14, 0x1A)  # PGA gain +30dB
    wr(0x15, 0x40)  # ADC settings
    wr(0x16, 0x24)  # ADC HPF
    wr(0x17, 0xBF)  # ADC volume MAX (unmuted)
    wr(0x1B, 0x0A)  # MIC boost
    wr(0x1C, 0x6A)  # ADC scale

    # GPIO config for ADC
    wr(0x44, 0x58)

    print("ES8311 ADC initialized!")

    # Verify key registers
    print("\nVerifying key registers:")
    checks = [
        (0x00, 0x80, "RESET"),
        (0x01, 0x3F, "CLK_MGR"),
        (0x17, 0xBF, "ADC_VOL"),
        (0x44, 0x58, "GPIO"),
    ]
    all_ok = True
    for reg, expected, name in checks:
        val = rd(reg)
        ok = "OK" if val == expected else "FAIL!"
        if val != expected:
            all_ok = False
        print(f"  {name}: 0x{val:02X} (expected 0x{expected:02X}) {ok}")

    return all_ok


def test_i2s(port=0, bits=16, fmt="mono", rate=16000):
    """Тест чтения I2S"""
    print(f"\nTesting I2S: port={port}, bits={bits}, format={fmt}, rate={rate}")

    if fmt == "mono":
        format = I2S.MONO
    elif fmt == "left":
        format = I2S.MONO  # MicroPython uses MONO for left channel
    else:
        format = I2S.STEREO

    try:
        i2s = I2S(
            port,
            sck=Pin(I2S_BCK),
            ws=Pin(I2S_WS),
            sd=Pin(I2S_DIN),
            mode=I2S.RX,
            bits=bits,
            format=format,
            rate=rate,
            ibuf=4096
        )

        buf = bytearray(512)
        i2s.readinto(buf)

        # Analyze data
        non_zero = sum(1 for b in buf if b != 0)
        print(f"  Read {len(buf)} bytes, non-zero: {non_zero}")
        print(f"  First 32 bytes: {list(buf[:32])}")

        # Calculate simple stats
        if bits == 16:
            import struct
            samples = struct.unpack('<' + 'h' * (len(buf) // 2), buf)
            min_s = min(samples)
            max_s = max(samples)
            print(f"  Sample range: {min_s} to {max_s}")

        i2s.deinit()
        return non_zero > 0

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_all_configs():
    """Тест всех комбинаций I2S настроек"""
    print("\n=== Testing all I2S configurations ===\n")

    # Сначала инициализируем ES8311
    init_es8311_adc()

    results = []

    for port in [0, 1]:
        for bits in [16, 32]:
            for fmt in ["mono", "stereo"]:
                ok = test_i2s(port=port, bits=bits, fmt=fmt)
                results.append((port, bits, fmt, ok))
                print()

    print("\n=== Results ===")
    for port, bits, fmt, ok in results:
        status = "DATA!" if ok else "zeros"
        print(f"  Port {port}, {bits}-bit, {fmt:6s}: {status}")


def quick_test():
    """Быстрый тест: init + read"""
    print("=== Quick Audio Test ===\n")

    # 1. Scan I2C
    scan()

    # 2. Init ES8311
    print()
    ok = init_es8311_adc()

    if not ok:
        print("\nWARNING: ES8311 init may have failed!")

    # 3. Test I2S
    print()
    test_i2s(port=0, bits=16, fmt="mono")
    test_i2s(port=1, bits=16, fmt="mono")


def monitor(duration_sec=5):
    """Мониторинг уровня микрофона"""
    import struct
    import time

    init_es8311_adc()

    i2s = I2S(
        0,
        sck=Pin(I2S_BCK),
        ws=Pin(I2S_WS),
        sd=Pin(I2S_DIN),
        mode=I2S.RX,
        bits=16,
        format=I2S.MONO,
        rate=16000,
        ibuf=4096
    )

    print(f"\nMonitoring mic for {duration_sec} seconds...")
    print("Speak into microphone!\n")

    buf = bytearray(512)
    start = time.time()
    max_level = 0

    while time.time() - start < duration_sec:
        i2s.readinto(buf)
        samples = struct.unpack('<' + 'h' * (len(buf) // 2), buf)
        rms = int((sum(s * s for s in samples) / len(samples)) ** 0.5)

        if rms > max_level:
            max_level = rms

        bar = '#' * min(50, rms // 100)
        print(f"\r{rms:5d} |{bar:<50}|", end='')

    i2s.deinit()
    print(f"\n\nMax level: {max_level}")

    if max_level < 10:
        print("WARNING: No audio detected! Microphone may not be working.")
    else:
        print("Audio detected!")


def test_pins():
    """Тест разных пинов для I2S DIN"""
    print("\n=== Testing different DIN pins ===\n")

    init_es8311_adc()

    # Возможные пины для данных микрофона
    possible_dins = [46, 42, 14, 39, 13, 15, 6, 7, 5]

    for din_pin in possible_dins:
        print(f"Testing DIN pin GPIO{din_pin}...", end=" ")
        try:
            i2s = I2S(
                0,
                sck=Pin(I2S_BCK),
                ws=Pin(I2S_WS),
                sd=Pin(din_pin),
                mode=I2S.RX,
                bits=16,
                format=I2S.MONO,
                rate=16000,
                ibuf=4096
            )

            buf = bytearray(256)
            i2s.readinto(buf)

            non_zero = sum(1 for b in buf if b != 0)
            i2s.deinit()

            if non_zero > 0:
                print(f"DATA! ({non_zero} non-zero bytes)")
                print(f"  First 16: {list(buf[:16])}")
            else:
                print("zeros")

        except Exception as e:
            print(f"ERROR: {e}")


def test_mclk():
    """Тест с генерацией MCLK через PWM"""
    from machine import PWM

    print("\n=== Testing with MCLK generation ===\n")

    # Возможные MCLK пины
    mclk_pins = [0, 2, 4]

    for mclk_pin in mclk_pins:
        print(f"\nTrying MCLK on GPIO{mclk_pin}...")

        try:
            # Генерируем MCLK = 256 * sample_rate = 256 * 16000 = 4.096 MHz
            pwm = PWM(Pin(mclk_pin), freq=4096000, duty=512)
            print(f"  MCLK PWM started at 4.096MHz")

            init_es8311_adc()

            i2s = I2S(
                0,
                sck=Pin(I2S_BCK),
                ws=Pin(I2S_WS),
                sd=Pin(I2S_DIN),
                mode=I2S.RX,
                bits=16,
                format=I2S.MONO,
                rate=16000,
                ibuf=4096
            )

            buf = bytearray(256)
            i2s.readinto(buf)

            non_zero = sum(1 for b in buf if b != 0)

            i2s.deinit()
            pwm.deinit()

            if non_zero > 0:
                print(f"  DATA! ({non_zero} non-zero bytes)")
                print(f"  First 16: {list(buf[:16])}")
                return mclk_pin
            else:
                print("  zeros")

        except Exception as e:
            print(f"  ERROR: {e}")
            try:
                pwm.deinit()
            except:
                pass

    return None


def raw_read():
    """Сырое чтение GPIO пина - проверка сигнала"""
    print("\n=== Raw GPIO read test ===")
    print("Reading GPIO46 (I2S_DIN) directly...")

    din = Pin(I2S_DIN, Pin.IN)

    # Читаем 100 значений
    values = [din.value() for _ in range(100)]
    ones = sum(values)

    print(f"  100 reads: {ones} ones, {100-ones} zeros")
    print(f"  Values: {values[:20]}...")

    if ones == 0 or ones == 100:
        print("  WARNING: Pin stuck at constant value!")
    else:
        print("  Pin is toggling - signal present")


# При импорте показываем подсказки
print("""
=== Audio Debug Module ===
Commands:
  scan()           - Scan I2C bus
  dump_regs()      - Dump ES8311 registers
  init_es8311_adc() - Initialize ES8311 for microphone
  test_i2s()       - Test I2S reading
  test_all_configs() - Test all I2S configurations
  quick_test()     - Quick test (recommended first)
  monitor(5)       - Monitor mic levels for 5 sec

  test_pins()      - Test different DIN pins
  test_mclk()      - Test with MCLK generation
  raw_read()       - Raw GPIO read test
""")

# Сборка MicroPython для Cardputer‑ADV: Мой реальный путь (macOS)

**Автор**: @kodinkod (Москва, 25.01.2026)  
**Цель**: MicroPython 1.27.0 + st7789 для M5Stack Cardputer‑ADV  
**История**: 50+ команд, 2 часа борьбы с ESP‑IDF 😅  

## 🎯 Что получилось
```
✅ MicroPython 1.27.0 + st7789 (дисплей)
✅ Прошито на Cardputer‑ADV (/dev/cu.usbmodem1101)
✅ Готово к диктофону + UI
```

## 📋 Пошаговый путь (мои команды)

### 1. Установка ESP‑IDF v5.5.2 (команды 2186–2205)
```bash
# Зависимости
brew install libgcrypt glib pixman sdl2 libslirp dfu-util cmake python
brew tap espressif/eim
eim install
xcode-select --install

# Клонируем ESP-IDF
mkdir -p ~/esp
cd ~/esp
git clone -b v5.5.2 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf

# Установка
./install.sh all
. $HOME/esp/esp-idf/export.sh  # ← Каждый раз!
idf.py  # Тест (должен работать)
```

### 2. Подготовка MicroPython + st7789 (2212–2216)
```bash
# Скачай MicroPython 1.27.0
cd /Users/kodin/Downloads/micropython-1.27.0/ports/esp32

# Скопируй .py модули st7789 (я делал вручную)
cp /Applications/programming/MicroPythonShell/st7789_mpy/st7789/*.py modules/

# Сборка
idf.py -D MICROPY_BOARD=ESP32_GENERIC_S3 \
       -D USER_C_MODULES=/Applications/programming/MicroPythonShell/st7789_mpy/st7789/micropython.cmake \
       build
```

### 3. Прошивка на Cardputer‑ADV (2217–2239)
```bash
# Порт
ls /dev/cu.* | grep usbmodem  # /dev/cu.usbmodem1101

# Цикл борьбы (я делал 10+ раз):
idf.py -p /dev/cu.usbmodem1101 erase_flash
idf.py -p /dev/cu.usbmodem1101 flash
idf.py -p /dev/cu.usbmodem1101 reset
idf.py -p /dev/cu.usbmodem1101 monitor
```

**Финальный рабочий набор**:
```bash
idf.py -p /dev/cu.usbmodem1101 erase_flash
idf.py -p /dev/cu.usbmodem1101 flash
idf.py -p /dev/cu.usbmodem1101 monitor  # Ждать 30 сек + Enter
```

## 🐛 Типичные проблемы (мой опыт)

| Симптом | Причина | Решение |
|---------|---------|---------|
| `CMakeLists.txt not found` | Неправильная папка | `cd ports/esp32` (НЕ modules!) |
| `waiting for download` | BOOT‑режим | Отключить USB → подключить БЕЗ BOOT |
| `filesystem corrupted` | Неполная FS | `erase_flash` + перепрошивка |
| `Device not configured` | USB‑кабель | Data cable (не charging!) |
| `idf.py monitor` висит | Медленный старт | `screen /dev/cu.usbmodem1101 115200` |

## 🚀 Результат

```
rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
MicroPython v1.27.0 on 2026-01-25
>>> import st7789  # ✅ Работает!
```

## 📂 Репозиторий
```
git init
git remote add origin https://github.com/kodinkod/MicroPython.git
```

**Теперь можно делать диктофон + UI на Microhydra!** 🎤✨  
#M5Stack #CardputerADV #MicroPython #ESP32S3

Источники

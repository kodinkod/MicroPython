# Сборка и прошивка MicroPython для Cardputer‑ADV (ESP32‑S3) на macOS

**Дата**: 25 января 2026  
**Устройство**: M5Stack Cardputer‑ADV (ESP32‑S3)  
**Версия MicroPython**: 1.27.0  
**Цель**: Сборка с модулем `st7789` (дисплей) + прошивка  

## Предварительные требования

```
✅ ESP-IDF v5.5.2 (~/esp/esp-idf)
✅ MicroPython 1.27.0 (скачан с micropython.org)
✅ esptool: pip3 install esptool
✅ Data USB‑кабель (не charging!)
✅ Драйвер CH9102/CP210x для macOS
✅ Порт: /dev/cu.usbmodem1101
```

## Шаг 1: Подготовка модулей

1. **Скачай/скопируй модуль st7789**:
   ```
   /Applications/programming/MicroPythonShell/st7789_mpy/st7789/
   ```

2. **Скопируй .py файлы**:
   ```bash
   cp /Applications/programming/MicroPythonShell/st7789_mpy/st7789/*.py \
      micropython-1.27.0/ports/esp32/modules/
   ```

## Шаг 2: Сборка прошивки

```bash
# Активируй ESP-IDF
source ~/esp/esp-idf/export.sh

# Перейди в папку сборки (ВАЖНО!)
cd micropython-1.27.0/ports/esp32

# Проверь CMakeLists.txt
ls CMakeLists.txt

# Собери для ESP32-S3 + st7789
idf.py -D MICROPY_BOARD=ESP32_GENERIC_S3 \
       -D USER_C_MODULES=/Applications/programming/MicroPythonShell/st7789_mpy/st7789/micropython.cmake \
       build
```

**Вывод успеха**:
```
Generated .../ports/esp32/build/micropython.bin
Project build complete.
```

## Шаг 3: Прошивка на Cardputer‑ADV

### Подготовка (ОБЯЗАТЕЛЬНО!)
```
1. Новый Data USB‑кабель
2. Зажми BOOT на Cardputer
3. Подключи USB (держи BOOT!)
4. Жди "Connecting..." (2–5 сек)
5. Отпусти BOOT
```

### Прошивка (esptool напрямую — надёжнее)
```bash
# 1. Найди порт
ls /dev/cu.usbmodem*

# 2. Сотри flash полностью
esptool.py --chip esp32s3 --port /dev/cu.usbmodem1101 erase_flash

# 3. Прошей (медленная скорость!)
esptool.py --chip esp32s3 \
           --port /dev/cu.usbmodem1101 \
           --baud 460800 \
           write_flash -z 0x10000 \
           micropython-1.27.0/ports/esp32/build/micropython.bin
```

### Проверка
```bash
# Monitor (ждём 30 сек, Enter)
idf.py -p /dev/cu.usbmodem1101 monitor

# Или screen (быстрее)
screen /dev/cu.usbmodem1101 115200
```

**Успех**:
```
rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
MicroPython v1.27.0 on 2026-01-25
>>> import st7789  # Работает!
```

## Типичные проблемы и решения

| Проблема | Решение |
|----------|---------|
| `waiting for download` (boot:0x23) | Hard reset: отключить USB → подключить БЕЗ BOOT |
| `filesystem corrupted` | `erase_flash` + перепрошивка |
| `Device not configured` | Новый data USB‑кабель, baud 460800 |
| `idf.py monitor` висит | screen /dev/cu.usbmodem1101 115200 |

## Следующие шаги

```
1. Тестируй st7789:
   >>> import st7789
   >>> help(st7789)

2. Создай /apps/ для Microhydra:
   >>> import os
   >>> os.mkdir("/apps")

3. Готов к диктофону + UI! 🎤
```

**Автор**: AI/ML Engineer, Москва 2026  
#M5Stack #CardputerADV #MicroPython #ESP32S3[1]

Источники
[1] ESP32-S3 https://micropython.org/download/ESP32_GENERIC_S3/

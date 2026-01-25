# MicroPython Shell for Cardputer ADV
[MicroPythonShell](mpy_shell_card_adv.png)

MicroPython Shell is a M5 Cardputer ADV(https://docs.m5stack.com/en/core/Cardputer-Adv) firmware for using MicroPython REPL through the device's built-in screen and keyboard. This firmward also include a text editor, allowing text file to be edited directly on the device.
This project is mainly coded in Python, and the screen driver comes from https://github.com/russhughes/st7789_mpy

## How to build
To build this firmware, you need to install esp-idf, and download the full MicroPython source code(https://micropython.org/download/) first.

After finishing above two steps, copy all `.py` files in the `modules` directory of this project to the `ports\esp32\modules` sub directory of micropython source code. Then execute the following command from the `ports\esp32` sub directory of micropython source code.

`idf.py -D MICROPY_BOARD=ESP32_GENERIC_S3 -D USER_C_MODULES=path/to/MicroPythonShell/st7789_mpy/st7789/micropython.cmake build`

## How to use
Use `edit()` to open text editor, `edit(filepath)` to edit a existing file. Press esc ( fn + ‵ ) to open menu in REPL and text editor. Press ctrl+[ ; . , / ] to scroll, fn+[ ; . , / ] to move cursor. Use `run(filepath)` to execute a Python file. Use `ls()`, `cd(path)`, `cwd()`, `mkdir()`, `rm(path)`, `rmdir(path)` to explore and modify the file system.

If you need to connect your device to Thonny, execute `dupterm() Stop` in the main menu first, and execute `dupterm() Start` after disconnect. If REPL has no respond, press ctrl+B.
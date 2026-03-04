import ctypes
import time
import pydirectinput
from datetime import datetime

# Проверка Caps Lock
def is_capslock_on():
    return bool(ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 1)

print("Запуск. Включи Caps Lock для старта, выключи — для остановки.")

while True:
    if is_capslock_on():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Нажимаю 'A'")
        pydirectinput.keyDown('a')
        time.sleep(0.05)
        pydirectinput.keyUp('a')
        time.sleep(0.05)

        if not is_capslock_on():
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Caps Lock выключен — остановка цикла.")
            continue

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Нажимаю 'D'")
        pydirectinput.keyDown('d')
        time.sleep(0.05)
        pydirectinput.keyUp('d')
        time.sleep(0.05)
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Caps Lock выключен — ожидание...")
        time.sleep(0.5)

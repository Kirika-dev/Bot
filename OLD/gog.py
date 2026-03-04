import pydirectinput  # <<< ИЗМЕНЕНИЕ 1: Импортируем новую библиотеку
import keyboard
import time
import ctypes

# ==============================================================================
# КОНФИГУРАЦИЯ
# ==============================================================================
CONFIG = {
    "keys_to_press": ['a', 'd'],
    "delay_between_keys": 0.001,
    "exit_key": 'q'
}

# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================================================

def is_capslock_on():
    """Проверяет состояние Caps Lock (работает только на Windows)."""
    return ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 1

# ==============================================================================
# ГЛАВНЫЙ ЦИКЛ
# ==============================================================================

def main():
    """Основная функция, управляющая логикой скрипта."""
    print("[INFO] Скрипт запущен.")
    print(f"[INFO] Включите Caps Lock для старта.")
    print(f"[INFO] Нажмите '{CONFIG['exit_key'].upper()}' для выхода из программы.")

    script_is_active = False
    print("\n[STATUS] Скрипт на паузе. Ожидание включения Caps Lock...")

    # Устанавливаем паузу для pydirectinput, чтобы избежать проблем
    pydirectinput.PAUSE = 0.001

    try:
        while True:
            if keyboard.is_pressed(CONFIG['exit_key']):
                break
            
            caps_lock_is_on = is_capslock_on()

            if caps_lock_is_on and not script_is_active:
                script_is_active = True
                print("\n[STATUS] Caps Lock включен. Скрипт АКТИВЕН.")
                # Даем секунду на переключение в игру
                time.sleep(1)

            elif not caps_lock_is_on and script_is_active:
                script_is_active = False
                print("\n[STATUS] Caps Lock выключен. Скрипт на ПАУЗЕ.")

            if script_is_active:
                for key in CONFIG['keys_to_press']:
                    # <<< ИЗМЕНЕНИЕ 2: Используем pydirectinput для нажатия
                    pydirectinput.press(key)
                    time.sleep(CONFIG['delay_between_keys'])
            else:
                time.sleep(0.1)

    except Exception as e:
        print(f"\n[ERROR] Произошла ошибка: {e}")
    finally:
        print(f"\n[EXIT] Нажата клавиша '{CONFIG['exit_key'].upper()}'. Скрипт завершён.")


if __name__ == "__main__":
    main()
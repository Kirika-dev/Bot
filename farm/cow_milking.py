import pydirectinput
import time
import ctypes

# ==============================================================================
# КОНФИГУРАЦИЯ ДОЕНИЯ КОРОВЫ
# ==============================================================================
CONFIG = {
    "keys_to_press": ['a', 'd'],
    "delay_between_keys": 0.05,  # Задержка между A и D (50мс)
    "delay_between_cycles": 0.4,  # Задержка между циклами (400мс)
    "exit_key": 'q'
}

# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================================================

def is_capslock_on():
    """Проверяет состояние Caps Lock (работает только на Windows)."""
    return ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 1

def press_key_safe(key):
    """Безопасное нажатие клавиши без влияния на системные настройки"""
    try:
        print(f"[DEBUG] Нажимаю клавишу: {key}")
        pydirectinput.press(key)
        print(f"[DEBUG] Клавиша {key} нажата")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка при нажатии {key}: {e}")
        return False

# ==============================================================================
# ГЛАВНЫЙ ЦИКЛ ДОЕНИЯ
# ==============================================================================

def main():
    """Основная функция авто доения коровы."""
    print("🐄 АВТО ДОЕНИЕ КОРОВЫ (БЕЗОПАСНАЯ ВЕРСИЯ)")
    print("=" * 50)
    print(f"⌨️  Клавиши: {' → '.join(CONFIG['keys_to_press'])}")
    print(f"⚡ Задержка между A и D: {CONFIG['delay_between_keys'] * 1000:.1f} мс")
    print(f"⏱️  Задержка между циклами: {CONFIG['delay_between_cycles'] * 1000:.1f} мс")
    print(f"🎯 Управление: Caps Lock для включения/выключения")
    print(f"🚪 Выход: Ctrl+C")
    print("=" * 50)
    
    print("\n[INFO] Скрипт запущен.")
    print(f"[INFO] Включите Caps Lock для старта.")
    print(f"[INFO] Нажмите Ctrl+C для выхода из программы.")

    script_is_active = False
    cycle_count = 0
    print("\n[STATUS] Скрипт на паузе. Ожидание включения Caps Lock...")

    try:
        while True:
            caps_lock_is_on = is_capslock_on()

            if caps_lock_is_on and not script_is_active:
                script_is_active = True
                cycle_count = 0
                print("\n[🐄] Caps Lock включен. Начинаю доение коровы...")
                print(f"[⚡] Задержка между клавишами: {CONFIG['delay_between_keys'] * 1000:.1f} мс")
                # Даем секунду на переключение в игру
                time.sleep(1)

            elif not caps_lock_is_on and script_is_active:
                script_is_active = False
                print("\n[⏸️] Caps Lock выключен. Доение приостановлено.")

            if script_is_active:
                cycle_count += 1
                print(f"\n[🔄] Цикл доения #{cycle_count}")
                
                # Доим корову - нажимаем клавиши по очереди
                for i, key in enumerate(CONFIG['keys_to_press']):
                    print(f"[{i+1}/{len(CONFIG['keys_to_press'])}] Нажимаю {key.upper()}")
                    
                    if press_key_safe(key):
                        print(f"[✅] {key.upper()} успешно нажата")
                    else:
                        print(f"[❌] Ошибка при нажатии {key.upper()}")
                    
                    # Задержка между клавишами (кроме последней)
                    if i < len(CONFIG['keys_to_press']) - 1:
                        print(f"[⏱️] Жду {CONFIG['delay_between_keys'] * 1000:.1f} мс...")
                        time.sleep(CONFIG['delay_between_keys'])
                
                print(f"[✅] Цикл #{cycle_count} завершен")
                print(f"[⏱️] Жду {CONFIG['delay_between_cycles'] * 1000:.1f} мс до следующего цикла...")
                time.sleep(CONFIG['delay_between_cycles'])  # Большая задержка между циклами
            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"\n[🏁] Доение завершено. Нажата Ctrl+C.")
        print(f"[📊] Всего выполнено циклов: {cycle_count}")
    except Exception as e:
        print(f"\n[❌] Произошла ошибка: {e}")
        print(f"[📊] Всего выполнено циклов: {cycle_count}")

if __name__ == "__main__":
    main()

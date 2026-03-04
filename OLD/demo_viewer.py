import pyautogui
import keyboard
import time
import random
import ctypes
import cv2
import numpy as np
import os

# ==============================================================================
# КОНФИГУРАЦИЯ
# ==============================================================================
CONFIG = {
    # --- Названия файлов с изображениями (должны лежать в той же папке) ---
    "knife_image": "knife.png",
    "veggies_image": "veggies.png",
    "cook_button_image": "cook.png",
    "target_slot_image": "slot.png",  # <<< ВАЖНО: Сделайте скриншот ПУСТОГО слота, куда нужно перетаскивать

    # --- Настройки поиска изображений ---
    "confidence_threshold": 0.85,  # Порог уверенности (от 0.0 до 1.0). Увеличьте, если есть ложные срабатывания.

    # --- Настройки времени и задержек (в секундах) ---
    "cooldown_between_cycles": 10,  # Пауза после одного цикла готовки
    "move_duration_range": (0.3, 0.6),  # Длительность движения мыши
    "click_delay_range": (0.1, 0.2),    # Пауза между нажатием и отпусканием кнопки мыши
    "action_delay_range": (0.2, 0.5),   # Случайная пауза между действиями

    # --- Клавиши управления ---
    "exit_key": "q",
}

# ==============================================================================
# ГЛОБАЛЬНЫЕ ФУНКЦИИ
# ==============================================================================

# Проверка состояния Caps Lock
def is_capslock_on():
    # Работает только на Windows
    return ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 1

# Загрузка и проверка шаблонов
def load_templates():
    print("[INFO] Загрузка изображений-шаблонов...")
    templates = {
        "knife": cv2.imread(CONFIG["knife_image"], cv2.IMREAD_GRAYSCALE),
        "veggies": cv2.imread(CONFIG["veggies_image"], cv2.IMREAD_GRAYSCALE),
        "cook": cv2.imread(CONFIG["cook_button_image"], cv2.IMREAD_GRAYSCALE),
        "target_slot": cv2.imread(CONFIG["target_slot_image"], cv2.IMREAD_GRAYSCALE)
    }
    # Проверяем, что все файлы загрузились
    for name, image in templates.items():
        if image is None:
            print(f"[ERROR] Не удалось загрузить изображение: '{CONFIG[name + '_image']}'. Убедитесь, что файл существует.")
            return None
    print("[SUCCESS] Шаблоны успешно загружены.")
    return templates

def find_random_point_in_template(template, confidence):
    """
    Ищет шаблон на экране и возвращает случайные координаты внутри найденной области.
    Это делает клики более человечными.
    """
    screenshot = pyautogui.screenshot()
    screen_rgb = np.array(screenshot)
    screen_gray = cv2.cvtColor(screen_rgb, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        h, w = template.shape
        # Находим верхний левый угол
        top_left = max_loc
        # Генерируем случайное смещение внутри найденного прямоугольника
        # (с небольшим отступом от краев, чтобы не промахнуться)
        random_x = top_left[0] + random.randint(int(w * 0.2), int(w * 0.8))
        random_y = top_left[1] + random.randint(int(h * 0.2), int(h * 0.8))
        return (random_x, random_y)
    return None

def human_like_move(to_x, to_y):
    """Плавное, "человеческое" движение мыши."""
    duration = random.uniform(*CONFIG["move_duration_range"])
    pyautogui.moveTo(to_x, to_y, duration=duration, tween=pyautogui.easeInOutQuad)

def human_like_drag(start_pos, end_pos):
    """Плавное, "человеческое" перетаскивание."""
    human_like_move(*start_pos)
    pyautogui.mouseDown()
    time.sleep(random.uniform(*CONFIG["click_delay_range"]))
    human_like_move(*end_pos)
    pyautogui.mouseUp()
    time.sleep(random.uniform(*CONFIG["click_delay_range"]))

# ==============================================================================
# ОСНОВНАЯ ЛОГИКА
# ==============================================================================

def perform_cooking_cycle(templates):
    """Выполняет один полный цикл действий: перетаскивание и готовка."""
    print("[RUNNING] Начало нового цикла готовки.")

    # 1. Находим динамически, куда перетаскивать
    target_slot_pos = find_random_point_in_template(templates["target_slot"], CONFIG["confidence_threshold"])
    if not target_slot_pos:
        print("[ERROR] Не найден слот для перетаскивания. Пропускаем цикл.")
        return False

    print(f"[INFO] Слот найден. Координаты: {target_slot_pos}")
    time.sleep(random.uniform(*CONFIG["action_delay_range"]))

    # 2. Перетаскиваем нож
    knife_pos = find_random_point_in_template(templates["knife"], CONFIG["confidence_threshold"])
    if knife_pos:
        print("[INFO] Перетаскиваю нож...")
        human_like_drag(knife_pos, target_slot_pos)
    else:
        print("[ERROR] Нож не найден на экране!")
        return False # Завершаем цикл, если что-то пошло не так
    
    time.sleep(random.uniform(*CONFIG["action_delay_range"]))

    # 3. Перетаскиваем овощи
    veggies_pos = find_random_point_in_template(templates["veggies"], CONFIG["confidence_threshold"])
    if veggies_pos:
        print("[INFO] Перетаскиваю овощи...")
        human_like_drag(veggies_pos, target_slot_pos)
    else:
        print("[ERROR] Овощи не найдены на экране!")
        return False

    time.sleep(random.uniform(*CONFIG["action_delay_range"]))

    # 4. Нажимаем кнопку "ГОТОВИТЬ"
    cook_pos = find_random_point_in_template(templates["cook"], CONFIG["confidence_threshold"])
    if cook_pos:
        print("[INFO] Нажимаю кнопку 'ГОТОВИТЬ'...")
        human_like_move(*cook_pos)
        pyautogui.click()
    else:
        print("[ERROR] Кнопка 'ГОТОВИТЬ' не найдена.")
        return False
        
    return True

# ==============================================================================
# ГЛАВНЫЙ ЦИКЛ
# ==============================================================================

def main():
    templates = load_templates()
    if not templates:
        # Если шаблоны не загрузились, скрипт не может продолжать работу
        input("Нажмите Enter для выхода...")
        return

    print("\n[INFO] Скрипт запущен.")
    print(f"[INFO] Включите Caps Lock для старта. Нажмите '{CONFIG['exit_key'].upper()}' для выхода.")
    
    try:
        while not keyboard.is_pressed(CONFIG['exit_key']):
            if is_capslock_on():
                if perform_cooking_cycle(templates):
                    print(f"[WAIT] Цикл завершен. Ждём {CONFIG['cooldown_between_cycles']} сек.")
                else:
                    print(f"[WAIT] В цикле произошла ошибка. Ждём {CONFIG['cooldown_between_cycles']} сек перед новой попыткой.")
                
                # Ожидание с возможностью досрочного выхода
                for _ in range(CONFIG['cooldown_between_cycles']):
                    if keyboard.is_pressed(CONFIG['exit_key']):
                        break
                    time.sleep(1)
            else:
                # Используем try-except, чтобы не печатать сообщение каждую секунду
                try:
                    # Ожидаем, пока не включат CapsLock или не нажмут выход
                    keyboard.wait(CONFIG['exit_key'], suppress=True, trigger_on_release=True)
                except (KeyError, keyboard.BlockingIOError):
                    # Это нормальное поведение, когда CapsLock включается
                    print("\n[PAUSED] Caps Lock выключен. Ожидание...")
                    # Небольшая пауза, чтобы избежать лишней нагрузки на процессор
                    time.sleep(0.5)
                    
    except KeyboardInterrupt:
        print("\n[STOPPED] Скрипт остановлен принудительно.")
    finally:
        print(f"\n[EXIT] Нажата '{CONFIG['exit_key'].upper()}'. Скрипт завершён.")


if __name__ == "__main__":
    main()
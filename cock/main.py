import sys
import pyautogui
import keyboard
import time
import random
import ctypes
import cv2
import numpy as np
import os # <-- Добавлен импорт os для работы с путями
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

# ==============================================================================
# GUI для выбора рецепта (без изменений)
# ==============================================================================
class RecipeSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выбор рецепта")
        self.setFixedSize(300, 200)

        self.current_recipe = "Овощной салат"

        layout = QVBoxLayout()

        self.label = QLabel(f"Текущий рецепт: {self.current_recipe}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.btn_smoothie = QPushButton("Выбрать Овощной смузи")
        self.btn_smoothie.clicked.connect(self.select_smoothie)
        layout.addWidget(self.btn_smoothie)

        self.btn_salad = QPushButton("Выбрать Овощной салат")
        self.btn_salad.clicked.connect(self.select_salad)
        layout.addWidget(self.btn_salad)

        self.setLayout(layout)

    def select_smoothie(self):
        self.current_recipe = "Овощной смузи"
        self.label.setText(f"Текущий рецепт: {self.current_recipe}")

    def select_salad(self):
        self.current_recipe = "Овощной салат"
        self.label.setText(f"Текущий рецепт: {self.current_recipe}")

# ==============================================================================
# Настройки под рецепты (без изменений)
# ==============================================================================
RECIPES = {
    "Овощной салат": {
        "items": ["knife.png", "veggies.png"],
        "target": "slot.png",
        "cook": "cook.png"
    },
    "Овощной смузи": {
        "items": ["corolla.png", "water.png", "veggies.png"],
        "target": "slot.png",
        "cook": "cook.png"
    }
}

CONFIG = {
    "confidence_threshold": 0.85,
    "cooldown_between_cycles_range": (1.5, 3),
    "move_duration_range": (0.12, 0.2),
    "click_delay_range": (0.03, 0.08),
    "action_delay_range": (0.08, 0.15),
    "exit_key_scancode": 16,
    "exit_key_name": "Q"
}

# ==============================================================================
# Вспомогательные функции
# ==============================================================================
def is_capslock_on():
    return ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 1

# === ИЗМЕНЕННАЯ ФУНКЦИЯ ЗАГРУЗКИ ШАБЛОНОВ ===
def load_templates(recipe_name):
    print(f"[INFO] Загрузка шаблонов для '{recipe_name}'...")
    
    # Получаем абсолютный путь к директории, где находится сам скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Вспомогательная функция для чтения файлов с путями, содержащими кириллицу (Unicode)
    def imread_unicode(path, flags):
        try:
            # Читаем файл как байтовый массив с помощью numpy
            img_np = np.fromfile(path, dtype=np.uint8)
            # Декодируем массив в изображение OpenCV
            img = cv2.imdecode(img_np, flags)
            return img
        except Exception:
            return None

    recipe = RECIPES[recipe_name]
    templates = {}

    # Загружаем все предметы
    for idx, item in enumerate(recipe["items"]):
        # Составляем полный, абсолютный путь к файлу изображения
        full_path = os.path.join(script_dir, item)
        img = imread_unicode(full_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"[ERROR] Не найден файл {item} по пути {full_path}")
            return None
        templates[f"item_{idx}"] = img

    # Цель
    full_path = os.path.join(script_dir, recipe["target"])
    target_img = imread_unicode(full_path, cv2.IMREAD_GRAYSCALE)
    if target_img is None:
        print(f"[ERROR] Не найден файл {recipe['target']} по пути {full_path}")
        return None
    templates["target"] = target_img

    # Кнопка готовки
    full_path = os.path.join(script_dir, recipe["cook"])
    cook_img = imread_unicode(full_path, cv2.IMREAD_GRAYSCALE)
    if cook_img is None:
        print(f"[ERROR] Не найден файл {recipe['cook']} по пути {full_path}")
        return None
    templates["cook"] = cook_img

    print("[SUCCESS] Все шаблоны загружены.")
    return templates

def find_random_point_in_template(template, confidence):
    screenshot = pyautogui.screenshot()
    screen_rgb = np.array(screenshot)
    screen_gray = cv2.cvtColor(screen_rgb, cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        h, w = template.shape
        top_left = max_loc
        random_x = top_left[0] + random.randint(int(w * 0.2), int(w * 0.8))
        random_y = top_left[1] + random.randint(int(h * 0.2), int(h * 0.8))
        return (random_x, random_y)
    return None

def human_like_move(to_x, to_y):
    duration = random.uniform(*CONFIG["move_duration_range"])
    if random.random() < 0.2:
        current_x, current_y = pyautogui.position()
        mid_x = (current_x + to_x) // 2 + random.randint(-5, 5)
        mid_y = (current_y + to_y) // 2 + random.randint(-5, 5)
        pyautogui.moveTo(mid_x, mid_y, duration=duration/2, tween=pyautogui.easeOutCubic)
        pyautogui.moveTo(to_x, to_y, duration=duration/2, tween=pyautogui.easeInCubic)
    else:
        pyautogui.moveTo(to_x, to_y, duration=duration, tween=pyautogui.easeOutCubic)
    if random.random() < 0.4:
        micro_x = random.randint(-1, 1)
        micro_y = random.randint(-1, 1)
        if abs(micro_x) > 0 or abs(micro_y) > 0:
            pyautogui.moveRel(micro_x, micro_y, duration=0.05, tween=pyautogui.easeOutQuad)

def human_like_drag(start_pos, end_pos):
    human_like_move(*start_pos)
    time.sleep(random.uniform(*CONFIG["click_delay_range"]))
    pyautogui.mouseDown()
    time.sleep(random.uniform(0.02, 0.06))
    human_like_move(*end_pos)
    pyautogui.mouseUp()
    time.sleep(random.uniform(*CONFIG["click_delay_range"]))

# ==============================================================================
# Основная логика (без изменений)
# ==============================================================================
def perform_cooking_cycle(templates):
    print("\n[RUNNING] Новый цикл...")
    target_slot_pos = find_random_point_in_template(templates["target"], CONFIG["confidence_threshold"])
    if not target_slot_pos:
        print("[ERROR] Не найден слот.")
        return False

    for key, template in templates.items():
        if key.startswith("item_"):
            pos = find_random_point_in_template(template, CONFIG["confidence_threshold"])
            if not pos:
                print(f"[ERROR] Не найден предмет {key}.")
                return False
            print(f"[INFO] Правый клик на {key}...")
            human_like_move(*pos)  # Подводим мышь
            time.sleep(random.uniform(*CONFIG["click_delay_range"]))  # Пауза перед кликом
            pyautogui.rightClick()  # <--- ВОТ ТВОЙ ПРАВЫЙ КЛИК!
            
            # Разные задержки (как было)
            if "knife" in key or "corolla" in key:
                delay = random.uniform(0.05, 0.1)
            else:
                delay = random.uniform(*CONFIG["action_delay_range"])
            time.sleep(delay)

    cook_pos = find_random_point_in_template(templates["cook"], CONFIG["confidence_threshold"])
    if not cook_pos:
        print("[ERROR] Кнопка 'Готовить' не найдена.")
        return False

    print("[INFO] Нажимаю 'Готовить'...")
    human_like_move(*cook_pos)
    pyautogui.click()
    return True
    
# ==============================================================================
# Главный цикл
# ==============================================================================
# === ИЗМЕНЕННАЯ ГЛАВНАЯ ФУНКЦИЯ ===
def main():
    app = QApplication(sys.argv)
    gui = RecipeSelector()
    gui.show()

    script_is_active = False
    last_recipe = None
    templates = None

    try:
        while True:
            app.processEvents()

            if last_recipe != gui.current_recipe:
                templates = load_templates(gui.current_recipe)
                last_recipe = gui.current_recipe
                
                # === ДОБАВЛЕНА ПРОВЕРКА ===
                # Если шаблоны не загрузились, прекращаем работу скрипта.
                if templates is None:
                    print("[FATAL] Не удалось загрузить шаблоны. Скрипт не может продолжать работу.")
                    # Даем пользователю 5 секунд, чтобы прочитать ошибку в консоли
                    time.sleep(5) 
                    break # Выходим из цикла while True

            caps_lock_is_on = is_capslock_on()

            if caps_lock_is_on and not script_is_active:
                script_is_active = True
                print("\n[STATUS] Caps Lock включен. Работаем...")

            elif not caps_lock_is_on and script_is_active:
                script_is_active = False
                print("\n[STATUS] Caps Lock выключен. Пауза.")

            if script_is_active:
                # Дополнительная проверка, чтобы скрипт не упал, если шаблоны не загружены
                if templates:
                    if perform_cooking_cycle(templates):
                        print("[SUCCESS] Цикл завершён.")
                    else:
                        print("[ERROR] Цикл прерван.")
                    cooldown = random.uniform(*CONFIG["cooldown_between_cycles_range"])
                    print(f"[WAIT] Кулдаун {cooldown:.1f} сек...")
                    time.sleep(cooldown)
                else:
                    # Если шаблоны не загружены, но Caps Lock включен, ставим на паузу
                    print("[PAUSE] Шаблоны не загружены. Проверьте файлы. Пауза...")
                    script_is_active = False
                    time.sleep(1) # Короткая пауза, чтобы не спамить в консоль
            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        print(f"\n[EXIT] Скрипт завершён.")

if __name__ == "__main__":
    main()

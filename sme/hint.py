import time
import ctypes
import os
import keyboard
import cv2
import mss
import numpy as np
import tkinter as tk

# --- Основные настройки ---
MONITOR_INDEX = 1
TEMPLATE_THRESHOLD = 0.7
UPDATE_RATE = 0.001  # не используется в цикле, можно убрать или применить

HARDCODED_ROI_CONFIG = {
    "rois": [
        {
            "x_norm": 0.4703125,
            "y_norm": 0.26481481481481484,
            "w_norm": 0.059895833333333336,
            "h_norm": 0.0962962962962963
        }
    ]
}

DEBUG = True
running = True

TEMPLATE_ACTIONS = [
    ("10.png", "7"), ("11.png", "9"), ("12.png", "6"),
    ("13.png", "4"), ("14.png", "3"), ("15.png", "1"),
    ("16.png", "2"), ("17.png", "6"), ("18.png", "10"),
    ("19.png", "0"), ("20.png", "1"), ("21.png", "5"),
]

class Overlay:
    def __init__(self):
        self.root = tk.Tk()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.config(bg="white")

        pos_x = screen_width - 150
        pos_y = (screen_height // 2) - 100
        self.root.geometry(f"+{pos_x}+{pos_y}")

        self.label = tk.Label(
            self.root, text="", font=("Arial", 80, "bold"),
            fg="red", bg="white"
        )
        self.label.pack()
        self.hide()

    def update_text(self, text):
        self.label.config(text=str(text))
        self.show()

    def show(self):
        self.root.deiconify()

    def hide(self):
        self.root.withdraw()

    def update(self):
        self.root.update_idletasks()
        self.root.update()

def log(message: str) -> None:
    if not DEBUG:
        return
    ts = time.strftime('%H:%M:%S')
    print(f"[{ts}] {message}")

def is_active() -> bool:
    try:
        return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)  # Caps Lock активен
    except Exception:
        return False

def stop_script():
    global running
    running = False

def compute_roi_rect_fixed(monitor_width, monitor_height, data):
    if not data or not data.get("rois"):
        return None
    first_roi = data["rois"][0]

    x_norm, y_norm, w_norm, h_norm = (
        first_roi["x_norm"],
        first_roi["y_norm"],
        first_roi["w_norm"],
        first_roi["h_norm"],
    )
    x = int(x_norm * monitor_width)
    y = int(y_norm * monitor_height)
    rw = int(w_norm * monitor_width)
    rh = int(h_norm * monitor_height)

    x = max(0, min(monitor_width - 1, x))
    y = max(0, min(monitor_height - 1, y))
    rw = max(1, min(monitor_width - x, rw))
    rh = max(1, min(monitor_height - y, rh))
    return (x, y, rw, rh)

def preload_templates():
    # Получаем директорию скрипта для правильного поиска изображений
    script_dir = os.path.dirname(os.path.abspath(__file__))
    loaded_templates = []
    
    for template_path, key in TEMPLATE_ACTIONS:
        # Ищем изображение в папке скрипта
        full_path = os.path.join(script_dir, template_path)
        if not os.path.exists(full_path):
            log(f"Шаблон не найден: {full_path}")
            continue
        template_img = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
        if template_img is not None:
            loaded_templates.append((template_img, key))
            log(f"Загружен шаблон: {template_path}")
        else:
            log(f"Не удалось загрузить шаблон: {template_path}")
    return loaded_templates

def press_sequence(number_str):
    """
    Нажимает клавишу '1', затем цифры из number_str с задержкой 0.25 секунды.
    Выводит в лог каждое нажатие.
    """
    log("Нажатие клавиши: '1'")
    keyboard.press_and_release('1')
    time.sleep(0.25)
    for ch in number_str:
        log(f"Нажатие клавиши: '{ch}'")
        keyboard.press_and_release(ch)
        time.sleep(0.25)

def main_loop(templates):
    global running
    overlay = Overlay()

    with mss.mss() as sct:
        mon = sct.monitors[MONITOR_INDEX]
        monitor_width = mon["width"]
        monitor_height = mon["height"]

        roi_rect = compute_roi_rect_fixed(monitor_width, monitor_height, HARDCODED_ROI_CONFIG)
        if roi_rect is None:
            print("Невозможно определить ROI.")
            return

        x, y, rw, rh = roi_rect

        last_pressed_key = None
        last_press_time = 0
        PRESS_COOLDOWN = 2.0  # секунд, чтобы не спамить нажатия

        while running:
            overlay.update()

            if not is_active():
                overlay.hide()
                time.sleep(1.0)
                continue

            monitor = {
                "top": mon["top"] + y,
                "left": mon["left"] + x,
                "width": rw,
                "height": rh,
            }
            sct_img = sct.grab(monitor)
            roi_img = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2GRAY)

            if roi_img.shape[0] < 1 or roi_img.shape[1] < 1:
                time.sleep(0.1)
                continue

            best_score = TEMPLATE_THRESHOLD
            best_match_key = None

            for template_img, confirmation_key in templates:
                if roi_img.shape[0] < template_img.shape[0] or roi_img.shape[1] < template_img.shape[1]:
                    continue

                res = cv2.matchTemplate(roi_img, template_img, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)

                if max_val > best_score:
                    best_score = max_val
                    best_match_key = confirmation_key

            now = time.time()
            if best_match_key is not None:
                log(f"Найдено лучшее совпадение: '{best_match_key}' со счетом {best_score:.3f}")

                if best_match_key != last_pressed_key or (now - last_press_time) > PRESS_COOLDOWN:
                    press_sequence(best_match_key)
                    last_pressed_key = best_match_key
                    last_press_time = now
                    overlay.update_text(best_match_key)
                    start = now
                    while time.time() - start < 0.5:
                        overlay.update()
                        time.sleep(0.01)
                else:
                    # Если совпадение то же и кулдаун не прошёл,
                    # просто обновим оверлей раз в 0.2 секунды и спим меньше
                    overlay.update()
                    time.sleep(0.2)
            else:
                overlay.hide()
                time.sleep(0.05)

    overlay.root.destroy()

if __name__ == "__main__":
    preloaded_templates = preload_templates()

    if preloaded_templates:
        keyboard.add_hotkey('ctrl+q', stop_script)
        main_loop(preloaded_templates)
    else:
        print("Нет загруженных шаблонов, выход.")

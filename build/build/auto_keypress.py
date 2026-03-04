import time
from pathlib import Path
from typing import Dict, List
import ctypes

import cv2  # type: ignore
import numpy as np  # type: ignore
import mss  # type: ignore
import pyautogui  # type: ignore


def load_template_with_search(image_name: str, base_dir: Path) -> np.ndarray:
    candidates: List[Path] = [
        base_dir / image_name,
        base_dir.parent / image_name,
        Path.cwd() / image_name,
    ]
    for candidate in candidates:
        if candidate.exists():
            template = cv2.imread(str(candidate), cv2.IMREAD_GRAYSCALE)
            if template is not None:
                return template
    tried = " | ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"Template not found: {image_name}. Tried: {tried}")


def press_key_quick(key: str) -> None:
    # Faster low-level key press for Windows
    key_to_vk: Dict[str, int] = {"e": 0x45, "f": 0x46, "h": 0x48}
    vk = key_to_vk.get(key.lower())
    if vk is None:
        pyautogui.press(key)
        return
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def is_capslock_on() -> bool:
    # VK_CAPITAL = 0x14; toggle state is lowest bit
    return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)


def main() -> None:
    script_dir = Path(__file__).resolve().parent

    # Configuration
    # Priority: check 'f' first for minimal latency
    image_to_key: Dict[str, str] = {
        "f.png": "f",
        "e.png": "e",
        "h.png": "h",
    }
    
    # Настройки точности распознавания (0.0 - 1.0)
    # Чем выше значение, тем точнее должно быть совпадение
    # Рекомендуемые значения:
    # - 0.85-0.90: Быстрое распознавание, возможны ложные срабатывания
    # - 0.90-0.95: Оптимальный баланс скорости и точности
    # - 0.95-0.98: Высокая точность, медленнее
    default_threshold: float = 0.92  # Общий порог для всех изображений
    per_image_threshold: Dict[str, float] = {
        "f.png": 0.90,  # Специальный порог для f.png
        "e.png": 0.92,  # Можно настроить индивидуально для каждого
        "h.png": 0.92   # изображения
    }
    
    cooldown_ms: int = 50   # tighter cooldown for faster repeats
    loop_sleep_s: float = 0.001

    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0

    # Load templates once (robust to being launched from nested folders)
    templates: Dict[str, np.ndarray] = {}
    for filename in image_to_key.keys():
        templates[filename] = load_template_with_search(filename, script_dir)

    last_sent_at_ms: Dict[str, int] = {key: 0 for key in image_to_key.values()}

    print("Starting in 3 seconds... Switch to your target window. Press Ctrl+C to stop.")
    time.sleep(3)

    with mss.mss() as sct:
        # Primary monitor only
        monitor = sct.monitors[1]

        previous_active = None  # type: ignore

        while True:
            now_ms = int(time.time() * 1000)

            active = is_capslock_on()
            if previous_active != active:
                if active:
                    print("Active: Caps Lock ON → detection running")
                else:
                    print("Paused: Caps Lock OFF → detection paused")
                previous_active = active

            if not active:
                time.sleep(0.05)
                continue

            # Capture screen and convert to grayscale
            frame = np.asarray(sct.grab(monitor))  # BGRA
            gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)

            # Scan templates in priority order; stop at first confident hit
            for filename, key in image_to_key.items():
                template = templates[filename]
                result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                _min_val, max_val, _min_loc, _max_loc = cv2.minMaxLoc(result)

                threshold = per_image_threshold.get(filename, default_threshold)
                
                # Логируем значения для отладки (можно отключить)
                if max_val > 0.7:  # Показываем только близкие совпадения
                    print(f"[DEBUG] {filename}: {max_val:.3f} >= {threshold:.3f}")
                
                if max_val >= threshold and (now_ms - last_sent_at_ms[key] >= cooldown_ms):
                    print(f"[MATCH] {filename}: {max_val:.3f} >= {threshold:.3f} → нажимаю '{key}'")
                    press_key_quick(key)
                    last_sent_at_ms[key] = now_ms
                    break

            time.sleep(loop_sleep_s)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass



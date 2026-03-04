import pyautogui
import time
import ctypes
import mss
import mss.tools
from PIL import Image
import os

def is_capslock_on():
    return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)

def get_scaling_factor():
    # Получаем DPI-масштаб для основного монитора (Windows)
    # Возвращает масштаб относительно 96 DPI (100%)
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()  # Для корректной работы DPI-запроса
    hdc = user32.GetDC(0)
    LOGPIXELSX = 88
    dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
    scaling = dpi_x / 96.0
    return scaling

def prepare_scaled_image(image_path, scaling):
    # Загружаем изображение и масштабируем
    original = Image.open(image_path)
    if scaling == 1.0:
        return image_path  # Масштаб 100%, не меняем
    else:
        new_size = (int(original.width * scaling), int(original.height * scaling))
        resized = original.resize(new_size, Image.LANCZOS)
        scaled_path = f"scaled_{int(scaling*100)}_{os.path.basename(image_path)}"
        resized.save(scaled_path)
        return scaled_path

def find_and_click(image_path, region=None, confidence=0.5):
    try:
        location = pyautogui.locateOnScreen(image_path, region=region, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            print(f"Найдено изображение {image_path} на позиции {center} в области {region}")
            pyautogui.click(center, duration=0)
            print("Клик выполнен.")
            return True
        else:
            print("Изображение не найдено — ждем появления...")
            return False
    except Exception as e:
        print("Ошибка при поиске:", e)
        return False

if __name__ == "__main__":
    # Область поиска (left, top, width, height)
    search_region = (1170, 425, 170, 365)

    scaling = get_scaling_factor()
    print(f"Масштаб экрана: {scaling*100:.1f}%")

    image_to_search = prepare_scaled_image('tax.png', scaling)

    import mss
    with mss.mss() as sct:
        img = sct.grab({'top': search_region[1], 'left': search_region[0], 'width': search_region[2], 'height': search_region[3]})
        mss.tools.to_png(img.rgb, img.size, output='search_region_screenshot.png')
    print("Скриншот области поиска сохранён как search_region_screenshot.png")

    pyautogui.PAUSE = 0
    pyautogui.MINIMUM_DURATION = 0

    print("Запуск. Поиск будет работать только при включённом Caps Lock.")
    while True:
        if is_capslock_on():
            find_and_click(image_to_search, region=search_region, confidence=0.5)
        else:
            print("Caps Lock выключен, ожидание...")
        time.sleep(0.5)

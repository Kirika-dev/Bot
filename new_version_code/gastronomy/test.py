import pyautogui
import threading
import time
from datetime import datetime

def get_mouse_coordinates():
    """Получает координаты мыши при нажатии правой кнопки"""
    try:
        import pynput
        from pynput import mouse
        
        def on_click(x, y, button, pressed):
            if button == mouse.Button.right and pressed:
                # Получаем экранные координаты
                screen_x, screen_y = pyautogui.position()
                
                # Форматируем время
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Выводим координаты в консоль
                print(f"[{timestamp}] Координаты: X={x}, Y={y} | Экранные: X={screen_x}, Y={screen_y}")
        
        print("Отслеживание координат мыши запущено...")
        print("Наведите мышь на нужное место и нажмите правую кнопку мыши")
        print("Для выхода нажмите Ctrl+C")
        print("-" * 50)
        
        # Создаем слушатель мыши
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
            
    except ImportError:
        print("Библиотека pynput не установлена. Установите: pip install pynput")
        print("Используется альтернативный метод...")
        alternative_tracking()

def alternative_tracking():
    """Альтернативный метод отслеживания без pynput"""
    print("Альтернативный метод отслеживания...")
    print("Нажмите Ctrl+C для выхода")
    
    try:
        while True:
            # Получаем позицию мыши
            x, y = pyautogui.position()
            
            # Проверяем нажатие правой кнопки
            if pyautogui.mouseDown(button='right'):
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Координаты: X={x}, Y={y}")
                time.sleep(0.1)  # Небольшая задержка
            
            time.sleep(0.01)  # Проверяем каждые 10мс
            
    except KeyboardInterrupt:
        print("\nОтслеживание остановлено")

if __name__ == "__main__":
    try:
        get_mouse_coordinates()
    except KeyboardInterrupt:
        print("\nПрограмма завершена")

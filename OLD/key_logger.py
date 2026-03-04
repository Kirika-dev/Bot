import keyboard
import time
import datetime
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Key, Listener

# ==============================================================================
# ЛОГГЕР КЛАВИШ
# ==============================================================================

class KeyLogger:
    def __init__(self):
        self.log_file = f"key_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.start_time = time.time()
        self.key_count = 0
        
    def on_press(self, key):
        """Обработчик нажатия клавиши"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        self.key_count += 1
        
        try:
            # Получаем название клавиши
            if hasattr(key, 'char'):
                key_name = key.char
            else:
                key_name = str(key)
            
            # Записываем в файл
            timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
            log_entry = f"[{timestamp}] +{key_name} (№{self.key_count}, +{elapsed:.3f}с)\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Выводим в консоль
            print(f"[{timestamp}] +{key_name} (№{self.key_count}, +{elapsed:.3f}с)")
            
        except Exception as e:
            print(f"Ошибка записи: {e}")
    
    def on_release(self, key):
        """Обработчик отпускания клавиши"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        try:
            if hasattr(key, 'char'):
                key_name = key.char
            else:
                key_name = str(key)
            
            timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
            log_entry = f"[{timestamp}] -{key_name} (+{elapsed:.3f}с)\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Проверяем выход
            if key == Key.esc:
                return False
                
        except Exception as e:
            print(f"Ошибка записи: {e}")

def main():
    print("🔍 ЛОГГЕР КЛАВИШ ДЛЯ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    print("📝 Записываю все нажатия клавиш в файл")
    print("⏱️  Время, номер нажатия, название клавиши")
    print("🚪 Нажмите ESC для выхода")
    print("=" * 50)
    
    # Создаем логгер
    logger = KeyLogger()
    
    print(f"\n📁 Лог сохраняется в: {logger.log_file}")
    print("🎯 Начинаю запись... Нажимайте любые клавиши!")
    print("=" * 50)
    
    # Запускаем прослушивание
    with Listener(
        on_press=logger.on_press,
        on_release=logger.on_release
    ) as listener:
        listener.join()
    
    print(f"\n✅ Запись завершена!")
    print(f"📊 Всего нажатий: {logger.key_count}")
    print(f"📁 Лог сохранен в: {logger.log_file}")

if __name__ == "__main__":
    main()

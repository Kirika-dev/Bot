import keyboard
import time
import datetime
import os

# ==============================================================================
# ПРОСТОЙ ЛОГГЕР КЛАВИШ
# ==============================================================================

class SimpleKeyLogger:
    def __init__(self):
        self.log_file = f"key_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.start_time = time.time()
        self.key_count = 0
        self.pressed_keys = set()
        
    def on_key_event(self, event):
        """Обработчик событий клавиатуры"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if event.event_type == keyboard.KEY_DOWN:
            # Нажатие клавиши
            if event.name not in self.pressed_keys:
                self.key_count += 1
                self.pressed_keys.add(event.name)
                
                timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                log_entry = f"[{timestamp}] +{event.name} (№{self.key_count}, +{elapsed:.3f}с)\n"
                
                # Записываем в файл
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                
                # Выводим в консоль
                print(f"[{timestamp}] +{event.name} (№{self.key_count}, +{elapsed:.3f}с)")
                
        elif event.event_type == keyboard.KEY_UP:
            # Отпускание клавиши
            if event.name in self.pressed_keys:
                self.pressed_keys.remove(event.name)
                
                timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                log_entry = f"[{timestamp}] -{event.name} (+{elapsed:.3f}с)\n"
                
                # Записываем в файл
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                
                # Выводим в консоль
                print(f"[{timestamp}] -{event.name} (+{elapsed:.3f}с)")

def main():
    print("🔍 ПРОСТОЙ ЛОГГЕР КЛАВИШ")
    print("=" * 50)
    print("📝 Записываю все нажатия клавиш в файл")
    print("⏱️  Время, номер нажатия, название клавиши")
    print("🚪 Нажмите Ctrl+C для выхода")
    print("=" * 50)
    
    # Создаем логгер
    logger = SimpleKeyLogger()
    
    print(f"\n📁 Лог сохраняется в: {logger.log_file}")
    print("🎯 Начинаю запись... Нажимайте любые клавиши!")
    print("=" * 50)
    
    try:
        # Регистрируем обработчик для всех клавиш
        keyboard.hook(logger.on_key_event)
        
        # Ждем прерывания
        keyboard.wait('ctrl+c')
        
    except KeyboardInterrupt:
        pass
    finally:
        # Отключаем хук
        keyboard.unhook_all()
        
        print(f"\n✅ Запись завершена!")
        print(f"📊 Всего нажатий: {logger.key_count}")
        print(f"📁 Лог сохранен в: {logger.log_file}")
        
        # Показываем содержимое файла
        if os.path.exists(logger.log_file):
            print(f"\n📄 Содержимое лога:")
            print("-" * 50)
            try:
                with open(logger.log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
            except Exception as e:
                print(f"Ошибка чтения файла: {e}")

if __name__ == "__main__":
    main()

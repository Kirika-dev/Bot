#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы ботов
"""

import os
import sys

def test_bot_files():
    """Проверяет наличие всех необходимых файлов ботов"""
    print("🔍 Проверка файлов ботов...")
    
    bots = [
        ("💊 Авто Лечение", "sme/hint.py"),
        ("🏗️ Авто Стройка", "build/build/auto_keypress.py"),
        ("🍳 Авто Готовка", "cock/main.py"),
        ("🚕 Авто Такси", "tax/find_click.py"),
        ("🐄 Авто Доение", "farm/cow_milking.py")
    ]
    
    all_good = True
    
    for name, path in bots:
        if os.path.exists(path):
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} - НЕ НАЙДЕН!")
            all_good = False
    
    return all_good

def test_dependencies():
    """Проверяет основные зависимости"""
    print("\n📦 Проверка зависимостей...")
    
    try:
        import PyQt6
        print("✅ PyQt6")
    except ImportError:
        print("❌ PyQt6 - не установлен")
        return False
    
    try:
        import cv2
        print("✅ OpenCV")
    except ImportError:
        print("❌ OpenCV - не установлен")
        return False
    
    try:
        import pyautogui
        print("✅ PyAutoGUI")
    except ImportError:
        print("❌ PyAutoGUI - не установлен")
        return False
    
    try:
        import numpy
        print("✅ NumPy")
    except ImportError:
        print("❌ NumPy - не установлен")
        return False
    
    return True

def main():
    print("🎮 Тестирование Игрового Бот Лаунчера")
    print("=" * 50)
    
    # Проверяем файлы
    files_ok = test_bot_files()
    
    # Проверяем зависимости
    deps_ok = test_dependencies()
    
    print("\n" + "=" * 50)
    if files_ok and deps_ok:
        print("🎉 Все проверки пройдены! Лаунчер готов к работе.")
        print("🚀 Запустите: python main_launcher.py")
    else:
        print("⚠️  Обнаружены проблемы:")
        if not files_ok:
            print("   - Некоторые файлы ботов не найдены")
        if not deps_ok:
            print("   - Установите зависимости: pip install -r requirements.txt")
    
    print("\n💡 Для запуска лаунчера используйте:")
    print("   python main_launcher.py")
    print("   или дважды кликните на run_launcher.bat")

if __name__ == "__main__":
    main()

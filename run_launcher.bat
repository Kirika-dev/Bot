@echo off
REM =================================================================
REM | Переключаем кодировку консоли на UTF-8 для корректного      |
REM | отображения кириллицы и эмодзи.                             |
REM =================================================================
chcp 65001 >nul

echo 🎮 Запуск Игрового Бот Лаунчера...
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

REM Проверяем наличие файла лаунчера
if not exist "main_launcher.py" (
    echo ❌ Файл main_launcher.py не найден!
    pause
    exit /b 1
)

REM Устанавливаем зависимости если нужно
if not exist "requirements.txt" (
    echo ⚠️ Файл requirements.txt не найден, пропускаем установку зависимостей
) else (
    echo 📦 Проверяем зависимости...
    pip install -r requirements.txt --quiet
)

echo 🚀 Запускаем лаунчер...
python main_launcher.py

if errorlevel 1 (
    echo.
    echo ❌ Произошла ошибка при запуске!
    echo 💡 Попробуйте установить зависимости: pip install -r requirements.txt
    pause
)
import os
os.environ["QT_LOGGING_RULES"] = "*.warning=false"

import sys
import subprocess
import signal
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFrame, QScrollArea, QGridLayout, 
                             QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class BotRunner(QThread):
    """Поток для запуска ботов"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, script_path):
        super().__init__()
        self.script_path = script_path
        self.process = None
        
    def run(self):
        try:
            # Запускаем скрипт в новом процессе
            self.process = subprocess.Popen([sys.executable, self.script_path])
            self.process.wait()  # Ждем завершения
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Неожиданная ошибка: {e}")
    
    def stop_bot(self):
        """Останавливает бота"""
        if self.process:
            try:
                # Отправляем сигнал завершения
                if os.name == 'nt':  # Windows
                    self.process.terminate()
                else:  # Linux/Mac
                    self.process.send_signal(signal.SIGTERM)
                
                # Ждем завершения
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # Принудительно завершаем
                self.process.kill()
            except Exception as e:
                print(f"Ошибка при остановке: {e}")
            finally:
                self.process = None

class BotCard(QFrame):
    """Карточка бота с информацией и кнопками запуска/остановки"""
    def __init__(self, title, description, script_path, category, icon_emoji):
        super().__init__()
        self.script_path = script_path
        self.runner = None
        self.setup_ui(title, description, category, icon_emoji)
        
    def setup_ui(self, title, description, category, icon_emoji):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.setMidLineWidth(1)
        self.setStyleSheet("""
            BotCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2b2b2b, stop:1 #1e1e1e);
                border: 2px solid #404040;
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
            }
            BotCard:hover {
                border-color: #007acc;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #323232, stop:1 #252525);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Заголовок с иконкой
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon_emoji)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setStyleSheet("margin-right: 10px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Категория
        category_label = QLabel(f"📁 {category}")
        category_label.setFont(QFont("Segoe UI", 11))
        category_label.setStyleSheet("color: #888888; margin-bottom: 10px;")
        layout.addWidget(category_label)
        
        # Описание
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet("color: #cccccc; margin-bottom: 20px; line-height: 1.4;")
        layout.addWidget(desc_label)
        
        # Кнопки запуска/остановки
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("🚀 Запустить")
        self.run_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007acc, stop:1 #005a9e);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005a9e, stop:1 #004578);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004578, stop:1 #003366);
            }
            QPushButton:disabled {
                background: #666666;
                color: #999999;
            }
        """)
        self.run_button.clicked.connect(self.run_bot)
        button_layout.addWidget(self.run_button)
        
        self.stop_button = QPushButton("⏹️ Остановить")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc3545, stop:1 #c82333);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c82333, stop:1 #bd2130);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bd2130, stop:1 #a71e2a);
            }
            QPushButton:disabled {
                background: #666666;
                color: #999999;
            }
        """)
        self.stop_button.clicked.connect(self.stop_bot)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def run_bot(self):
        if os.path.exists(self.script_path):
            self.run_button.setEnabled(False)
            self.run_button.setText("⏳ Запуск...")
            self.stop_button.setEnabled(False)
            
            # Создаем и запускаем поток
            self.runner = BotRunner(self.script_path)
            self.runner.finished.connect(self.on_finished)
            self.runner.error.connect(self.on_error)
            self.runner.start()
            
            # Обновляем интерфейс
            self.run_button.setText("🔄 Работает")
            self.stop_button.setEnabled(True)
        else:
            QMessageBox.warning(None, "Ошибка", f"Файл не найден: {self.script_path}")
    
    def stop_bot(self):
        """Останавливает бота"""
        if self.runner:
            self.runner.stop_bot()
            self.runner.quit()
            self.runner.wait()
            self.runner = None
            
            # Обновляем интерфейс
            self.run_button.setEnabled(True)
            self.run_button.setText("🚀 Запустить")
            self.stop_button.setEnabled(False)
    
    def on_finished(self):
        self.run_button.setEnabled(True)
        self.run_button.setText("🚀 Запустить")
        self.stop_button.setEnabled(False)
        self.runner = None
        
    def on_error(self, error_msg):
        self.run_button.setEnabled(True)
        self.run_button.setText("🚀 Запустить")
        self.stop_button.setEnabled(False)
        self.runner = None
        QMessageBox.critical(None, "Ошибка", error_msg)

class MainLauncher(QMainWindow):
    """Главное окно лаунчера"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_bots()
        
    def setup_ui(self):
        self.setWindowTitle("🎮 Игровой Бот Лаунчер")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #0f0f0f);
            }
            QLabel {
                color: #ffffff;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007acc, stop:1 #005a9e);
                border-radius: 7px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005a9e, stop:1 #004578);
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Заголовок
        header_label = QLabel("🎮 Игровой Бот Лаунчер")
        header_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("""
            color: #007acc;
            margin-bottom: 15px;
        """)
        main_layout.addWidget(header_label)
        
        # Подзаголовок
        subtitle_label = QLabel("Выберите бота для автоматизации игрового процесса")
        subtitle_label.setFont(QFont("Segoe UI", 14))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #888888; margin-bottom: 25px;")
        main_layout.addWidget(subtitle_label)
        
        # Область с ботами
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.bots_container = QWidget()
        self.bots_layout = QGridLayout(self.bots_container)
        self.bots_layout.setSpacing(20)
        
        scroll_area.setWidget(self.bots_container)
        main_layout.addWidget(scroll_area)
        
        # Информация внизу
        info_label = QLabel("💡 Управление: Caps Lock для включения/выключения ботов")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666666; font-size: 11px; margin-top: 15px;")
        main_layout.addWidget(info_label)
        
    def setup_bots(self):
        """Настройка списка ботов"""
        bots = [
            {
                "title": "Авто Лечение",
                "description": "Автоматически распознает изображения на экране и показывает подсказки для лечения в оверлее. Использует компьютерное зрение для поиска совпадений.",
                "script_path": "sme/hint.py",
                "category": "Лечение",
                "icon_emoji": "💊"
            },
            {
                "title": "Авто Стройка",
                "description": "Автоматическое нажатие кнопок на стройке. Выполняет последовательность действий для автоматизации строительных процессов в игре.",
                "script_path": "build/build/auto_keypress.py",
                "category": "Строительство",
                "icon_emoji": "🏗️"
            },
            {
                "title": "Авто Готовка",
                "description": "Автоматизирует процесс готовки в игре. Поддерживает выбор рецептов (овощной салат, смузи) с GUI интерфейсом для настройки.",
                "script_path": "cock/main.py",
                "category": "Готовка",
                "icon_emoji": "🍳"
            },
            {
                "title": "Авто Такси",
                "description": "Автоматически находит и ловит заказы такси в заданной области экрана. Использует распознавание изображений для поиска новых заказов.",
                "script_path": "tax/find_click.py",
                "category": "Такси",
                "icon_emoji": "🚕"
            },
            {
                "title": "Авто Доение",
                "description": "Автоматическое доение коровы на ферме. Быстро нажимает клавиши A и D для эффективного сбора молока. Настраиваемая скорость доения.",
                "script_path": "farm/cow_milking.py",
                "category": "Ферма",
                "icon_emoji": "🐄"
            }
        ]
        
        # Размещаем ботов в сетке
        row, col = 0, 0
        max_cols = 2
        
        for bot_info in bots:
            bot_card = BotCard(
                bot_info["title"],
                bot_info["description"],
                bot_info["script_path"],
                bot_info["category"],
                bot_info["icon_emoji"]
            )
            
            self.bots_layout.addWidget(bot_card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

def main():
    # Возвращаем функцию main к её исходному виду
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    launcher = MainLauncher()
    launcher.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
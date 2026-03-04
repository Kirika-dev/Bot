import sys
import time
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QFrame, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
import pyautogui

# Глобальная переменная для состояния Caps Lock
CAPS_LOCK_STATE = False

def start_caps_lock_monitor():
    """Запускает мониторинг Caps Lock в отдельном потоке"""
    try:
        import pynput
        from pynput import keyboard
        
        def on_press(key):
            global CAPS_LOCK_STATE
            if key == keyboard.Key.caps_lock:
                CAPS_LOCK_STATE = True
                print(f"[{time.strftime('%H:%M:%S')}] Caps Lock ВКЛЮЧЕН (глобально)")
        
        def on_release(key):
            global CAPS_LOCK_STATE
            if key == keyboard.Key.caps_lock:
                CAPS_LOCK_STATE = False
                print(f"[{time.strftime('%H:%M:%S')}] Caps Lock ВЫКЛЮЧЕН (глобально)")
        
        # Запускаем мониторинг в отдельном потоке
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        print(f"[{time.strftime('%H:%M:%S')}] Мониторинг Caps Lock запущен")
        return listener
        
    except ImportError:
        print(f"[{time.strftime('%H:%M:%S')}] Библиотека pynput не установлена")
        return None

class AutomationThread(QThread):
    """Поток для автоматизации кликов"""
    finished_signal = pyqtSignal()
    caps_lock_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.caps_lock_active = False
        self.coordinates = [
            (690, 576, "right"),   # Правый клик
            (1165, 291, "right"),  # Правый клик
            (807, 674, "left")     # Левый клик
        ]
        
    def set_caps_lock_state(self, active):
        """Устанавливает состояние Caps Lock"""
        print(f"[{time.strftime('%H:%M:%S')}] Устанавливаю Caps Lock: {active}")
        self.caps_lock_active = active
        
    def run(self):
        self.running = True
        
        while self.running:
            # Проверяем глобальное состояние Caps Lock
            global CAPS_LOCK_STATE
            if CAPS_LOCK_STATE:
                print(f"[{time.strftime('%H:%M:%S')}] Caps Lock активен - начинаю выполнение")
                
                # Выполняем ВСЮ последовательность кликов БЕЗ прерывания
                for i, (x, y, click_type) in enumerate(self.coordinates):
                    if not self.running:
                        break
                    
                    print(f"[{time.strftime('%H:%M:%S')}] Клик {i+1}: ({x}, {y}) - {click_type}")
                    # Перемещаем мышь и кликаем
                    pyautogui.moveTo(x, y, duration=0.1)
                    
                    if click_type == "right":
                        pyautogui.rightClick()
                    else:
                        pyautogui.click()
                    
                    time.sleep(0.2)  # Небольшая пауза между кликами
                
                print(f"[{time.strftime('%H:%M:%S')}] Все клики выполнены")
                
                # Ждем 5 секунд перед повторением
                print(f"[{time.strftime('%H:%M:%S')}] Ожидание 5 секунд перед повторением")
                for i in range(5):
                    if not self.running:
                        break
                    time.sleep(1)
                
                print(f"[{time.strftime('%H:%M:%S')}] Ожидание завершено, готов к повторению")
                
                # НЕ выходим из цикла - он автоматически повторится
                # Продолжаем выполнение while цикла
            else:
                time.sleep(0.1)  # Быстрая реакция на включение Caps Lock
        
        self.finished_signal.emit()
    
    def stop(self):
        self.running = False

class ModernButton(QPushButton):
    """Современная кнопка с минималистичным дизайном"""
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.primary = primary
        self.setup_style()
        
    def setup_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #6366f1;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #5855eb;
                }
                QPushButton:pressed {
                    background-color: #4f46e5;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f3f4f6;
                    color: #374151;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #e5e7eb;
                }
                QPushButton:pressed {
                    background-color: #d1d5db;
                }
            """)

class GastronomyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.automation_thread = None
        self.dragging = False
        self.offset = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Gastronomy")
        self.setGeometry(100, 100, 450, 450)
        self.setMinimumSize(617, 843)  # Устанавливаем минимальный размер окна
        
        # Определяем разрешение экрана
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Получаем информацию о всех экранах
        screens = QApplication.screens()
        print(f"[{time.strftime('%H:%M:%S')}] Количество экранов: {len(screens)}")
        print(f"[{time.strftime('%H:%M:%S')}] Основной экран: {screen_width}x{screen_height}")
        
        # Выводим информацию о каждом экране
        for i, screen in enumerate(screens):
            geometry = screen.geometry()
            dpi = screen.logicalDotsPerInch()
            print(f"[{time.strftime('%H:%M:%S')}] Экран {i+1}: {geometry.width()}x{geometry.height()} (x:{geometry.x()}, y:{geometry.y()}) DPI: {dpi}")
        
        print(f"[{time.strftime('%H:%M:%S')}] Размер окна приложения: {self.width()}x{self.height()}")
        print(f"[{time.strftime('%H:%M:%S')}] Минимальный размер окна: 617x843")
        
        # Убираем стандартный title bar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Включаем отслеживание событий клавиатуры
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Кастомный title bar
        title_bar = QFrame()
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        title_bar.setFixedHeight(50)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        # Иконка и заголовок
        title_icon = QLabel("🍽️")
        title_icon.setFont(QFont("Segoe UI", 16))
        title_layout.addWidget(title_icon)
        
        title_text = QLabel("Gastronomy")
        title_text.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        title_text.setStyleSheet("color: #1e293b;")
        title_layout.addWidget(title_text)
        
        # Делаем title bar перетаскиваемым
        title_bar.mousePressEvent = self.title_bar_mouse_press
        title_bar.mouseMoveEvent = self.title_bar_mouse_move
        title_bar.mouseReleaseEvent = self.title_bar_mouse_release
        
        title_layout.addStretch()
        
        # Кнопки управления окном
        min_button = QPushButton("─")
        min_button.setFixedSize(30, 30)
        min_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 15px;
                color: #64748b;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #475569;
            }
        """)
        min_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_button)
        
        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 15px;
                color: #64748b;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: white;
            }
        """)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)
        
        main_layout.addWidget(title_bar)
        
        # Основной контент
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
            }
        """)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(18, 18, 18, 18)
        
        # Карточка выбора блюда
        dish_card = QFrame()
        dish_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                padding: 15px;
            }
        """)
        dish_layout = QVBoxLayout(dish_card)
        dish_layout.setSpacing(10)
        
        # Выбор блюда
        dish_label = QLabel("Текущее блюдо:")
        dish_label.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        dish_label.setStyleSheet("color: #1e293b; margin-bottom: 10px; font-weight: 600;")
        dish_layout.addWidget(dish_label)
        dish_layout.addSpacing(15)
        
        self.dish_combo = QComboBox()
        self.dish_combo.addItem("🥗 Овощной салат")
        self.dish_combo.addItem("🥤 Овощной смузи")
        self.dish_combo.addItem("🍅 Салат Капрезе")
        self.dish_combo.addItem("🐟 Сашими из фугу")
        self.dish_combo.addItem("🥘 Рагу")
        self.dish_combo.setCurrentText("🥗 Овощной салат")  # Устанавливаем текст по умолчанию
        self.dish_combo.currentTextChanged.connect(self.on_dish_changed)  # Подключаем обработчик изменения
        self.dish_combo.setFont(QFont("Segoe UI", 11))
        self.dish_combo.setEnabled(False)  # Отключаем возможность клика
        self.dish_combo.setStyleSheet("""
            QComboBox {
                background-color: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
                color: #64748b;
                font-weight: 500;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 0px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
                width: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                selection-background-color: #f3f4f6;
                outline: none;
            }
        """)
        # Создаем layout для блюда с навигацией
        dish_navigation_layout = QHBoxLayout()
        dish_navigation_layout.setSpacing(12)
        
        # Кнопка "назад"
        # Кнопка "назад"
        self.prev_dish_button = ModernButton("←")
        self.prev_dish_button.setFixedSize(45, 35)
        self.prev_dish_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #475569;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        self.prev_dish_button.clicked.connect(self.previous_dish)
        dish_navigation_layout.addWidget(self.prev_dish_button)
        
        # ComboBox по центру (занимает все доступное пространство)
        dish_navigation_layout.addWidget(self.dish_combo, 1)
        
        # Кнопка "вперед"
        self.next_dish_button = ModernButton("→")
        self.next_dish_button.setFixedSize(45, 35)
        self.next_dish_button.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #475569;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        self.next_dish_button.clicked.connect(self.next_dish)
        dish_navigation_layout.addWidget(self.next_dish_button)
        
        dish_layout.addLayout(dish_navigation_layout)
        dish_layout.addSpacing(10)
        
        # Кнопка подтверждения
        self.confirm_button = ModernButton("Подтвердить выбор", primary=True)
        self.confirm_button.clicked.connect(self.confirm_selection)
        dish_layout.addWidget(self.confirm_button)
        dish_layout.addSpacing(5)
        
        content_layout.addWidget(dish_card)
        content_layout.addSpacing(15)
        
        # Карточка управления
        control_card = QFrame()
        control_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                padding: 15px;
            }
        """)
        control_layout = QVBoxLayout(control_card)
        control_layout.setSpacing(10)
        
        # Заголовок с информацией об ингредиентах
        self.ingredients_title = QLabel("🥗 Овощной салат: У вас должны быть только Овощи")
        self.ingredients_title.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.ingredients_title.setStyleSheet("color: #1e293b; margin-bottom: 10px; font-weight: 600;")
        control_layout.addWidget(self.ingredients_title)
        control_layout.addSpacing(15)
        
        # Инструкции
        instructions = QLabel("""
        • Выберите блюдо из списка выше
        • Нажмите "Запустить автоматизацию"
        • Включите Caps Lock для начала действий
        • Выключите Caps Lock для остановки
        • Автоматизация будет повторяться циклически
        """)
        instructions.setFont(QFont("Segoe UI", 11))
        instructions.setStyleSheet("color: #64748b; margin-bottom: 15px; line-height: 1.5;")
        instructions.setWordWrap(True)
        control_layout.addWidget(instructions)
        control_layout.addSpacing(15)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = ModernButton("▶️ Запустить автоматизацию", primary=True)
        self.start_button.clicked.connect(self.start_automation)
        self.start_button.setEnabled(False)  # Изначально отключена
        button_layout.addWidget(self.start_button)
        
        self.stop_button = ModernButton("⏹️ Остановить")
        self.stop_button.clicked.connect(self.stop_automation)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        # Тестовая кнопка для проверки автоматизации
        self.test_button = ModernButton("🧪 Тест автоматизации")
        self.test_button.clicked.connect(self.test_automation)
        button_layout.addWidget(self.test_button)
        
        control_layout.addLayout(button_layout)
        control_layout.addSpacing(5)
        content_layout.addWidget(control_card)
        content_layout.addSpacing(15)
        
        # Статус
        self.status_label = QLabel("✅ Выбрано: 🥗 Овощной салат")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #059669; padding: 10px; background-color: #d1fae5; border-radius: 8px;")
        content_layout.addWidget(self.status_label)
        
        # Добавляем контент в главный layout
        main_layout.addWidget(content_widget)
        
    def on_dish_changed(self):
        """Обработчик изменения выбора блюда"""
        selected_dish = self.dish_combo.currentText()
        
        # Обновляем информацию об ингредиентах
        if selected_dish == "🥗 Овощной салат":
            self.ingredients_title.setText("🥗 Овощной салат: У вас должны быть только Овощи")
            self.status_label.setText(f"✅ Выбрано: {selected_dish}")
            self.status_label.setStyleSheet("color: #059669; padding: 10px; background-color: #d1fae5; border-radius: 8px;")
            self.start_button.setEnabled(True)
        elif selected_dish == "🥤 Овощной смузи":
            self.ingredients_title.setText("🥤 Овощной смузи: У вас должны быть только Овощи")
            self.status_label.setText(f"⚠️ {selected_dish} - пока не поддерживается")
            self.status_label.setStyleSheet("color: #d97706; padding: 10px; background-color: #fef3c7; border-radius: 8px;")
            self.start_button.setEnabled(False)
        elif selected_dish == "🍅 Салат Капрезе":
            self.ingredients_title.setText("🍅 Салат Капрезе: У вас должны быть только Сыр и Овощи")
            self.status_label.setText(f"⚠️ {selected_dish} - пока не поддерживается")
            self.status_label.setStyleSheet("color: #d97706; padding: 10px; background-color: #fef3c7; border-radius: 8px;")
            self.start_button.setEnabled(False)
        elif selected_dish == "🐟 Сашими из фугу":
            self.ingredients_title.setText("🐟 Сашими из фугу: У вас должны быть только Фугу")
            self.status_label.setText(f"⚠️ {selected_dish} - пока не поддерживается")
            self.status_label.setStyleSheet("color: #d97706; padding: 10px; background-color: #fef3c7; border-radius: 8px;")
            self.start_button.setEnabled(False)
        elif selected_dish == "🥘 Рагу":
            self.ingredients_title.setText("🥘 Рагу: У вас должны быть только Овощи и Мясо")
            self.status_label.setText(f"⚠️ {selected_dish} - пока не поддерживается")
            self.status_label.setStyleSheet("color: #d97706; padding: 10px; background-color: #fef3c7; border-radius: 8px;")
            self.start_button.setEnabled(False)
            
    def confirm_selection(self):
        selected_dish = self.dish_combo.currentText()
        if selected_dish == "🥗 Овощной салат":
            self.status_label.setText(f"✅ Выбрано: {selected_dish}")
            self.status_label.setStyleSheet("color: #059669; padding: 10px; background-color: #d1fae5; border-radius: 8px;")
            self.start_button.setEnabled(True)
        else:
            self.status_label.setText(f"⚠️ {selected_dish} - пока не поддерживается")
            self.status_label.setStyleSheet("color: #d97706; padding: 10px; background-color: #fef3c7; border-radius: 8px;")
            self.start_button.setEnabled(False)
        
    def start_automation(self):
        selected_dish = self.dish_combo.currentText()
        if selected_dish != "🥗 Овощной салат":
            self.status_label.setText("❌ Автоматизация недоступна для этого блюда")
            self.status_label.setStyleSheet("color: #dc2626; padding: 10px; background-color: #fee2e2; border-radius: 8px;")
            return
            
        if self.automation_thread is None or not self.automation_thread.isRunning():
            self.automation_thread = AutomationThread()
            self.automation_thread.finished_signal.connect(self.on_automation_finished)
            self.automation_thread.start()
            
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("🚀 Автоматизация активна - включите Caps Lock")
            self.status_label.setStyleSheet("color: #dc2626; padding: 10px; background-color: #fee2e2; border-radius: 8px;")
            
    def stop_automation(self):
        if self.automation_thread and self.automation_thread.isRunning():
            self.automation_thread.stop()
            self.automation_thread.wait()
            
        # Проверяем, какое блюдо выбрано
        selected_dish = self.dish_combo.currentText()
        if selected_dish == "🥗 Овощной салат":
            self.start_button.setEnabled(True)
            self.status_label.setText("⏹️ Автоматизация остановлена")
            self.status_label.setStyleSheet("color: #059669; padding: 10px; background-color: #d1fae5; border-radius: 8px;")
        else:
            self.start_button.setEnabled(False)
            self.status_label.setText(f"⚠️ {selected_dish} - пока не поддерживается")
            self.status_label.setStyleSheet("color: #d97706; padding: 10px; background-color: #fef3c7; border-radius: 8px;")
            
        self.stop_button.setEnabled(False)
        
    def previous_dish(self):
        """Переход к предыдущему блюду"""
        current_index = self.dish_combo.currentIndex()
        if current_index > 0:
            self.dish_combo.setCurrentIndex(current_index - 1)
        
    def next_dish(self):
        """Переход к следующему блюду"""
        current_index = self.dish_combo.currentIndex()
        if current_index < self.dish_combo.count() - 1:
            self.dish_combo.setCurrentIndex(current_index + 1)
        
    def on_automation_finished(self):
        # Проверяем, какое блюдо выбрано
        selected_dish = self.dish_combo.currentText()
        if selected_dish == "🥗 Овощной салат":
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
    
    def test_automation(self):
        """Тестирует автоматизацию без Caps Lock"""
        print(f"[{time.strftime('%H:%M:%S')}] Тестирую автоматизацию...")
        if self.automation_thread and self.automation_thread.isRunning():
            print(f"[{time.strftime('%H:%M:%S')}] Включаю тестовый режим")
            self.automation_thread.set_caps_lock_state(True)
            # Через 10 секунд выключаем тест
            QTimer.singleShot(10000, lambda: self.automation_thread.set_caps_lock_state(False))
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Автоматизация не запущена!")
        

        
    def title_bar_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
    
    def title_bar_mouse_move(self, event):
        if self.dragging and self.offset:
            new_pos = event.globalPosition().toPoint() - self.offset
            self.move(new_pos)
    
    def title_bar_mouse_release(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.offset = None
    
    def closeEvent(self, event):
        if self.automation_thread and self.automation_thread.isRunning():
            self.automation_thread.stop()
            self.automation_thread.wait()
        event.accept()
    
    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        new_size = event.size()
        print(f"[{time.strftime('%H:%M:%S')}] Размер окна изменен: {new_size.width()}x{new_size.height()}")
        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        """Обработчик нажатия клавиш"""
        key_code = event.key()
        print(f"[{time.strftime('%H:%M:%S')}] Нажата клавиша: {key_code} (Caps Lock = {Qt.Key.Key_CapsLock})")
        
        # Проверяем оба возможных кода Caps Lock
        if key_code == Qt.Key.Key_CapsLock or key_code == 16777251:
            print(f"[{time.strftime('%H:%M:%S')}] Caps Lock нажат!")
            if self.automation_thread and self.automation_thread.isRunning():
                self.automation_thread.set_caps_lock_state(True)
                print(f"[{time.strftime('%H:%M:%S')}] Caps Lock включен - автоматизация активна")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Автоматизация НЕ запущена!")
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Обработчик отпускания клавиш"""
        key_code = event.key()
        print(f"[{time.strftime('%H:%M:%S')}] Отпущена клавиша: {key_code}")
        
        # Проверяем оба возможных кода Caps Lock
        if key_code == Qt.Key.Key_CapsLock or key_code == 16777251:
            print(f"[{time.strftime('%H:%M:%S')}] Caps Lock отпущен!")
            if self.automation_thread and self.automation_thread.isRunning():
                self.automation_thread.set_caps_lock_state(False)
                print(f"[{time.strftime('%H:%M:%S')}] Caps Lock выключен - автоматизация приостановлена")
        super().keyReleaseEvent(event)

def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyle('Fusion')
    
    # Запускаем мониторинг Caps Lock
    caps_lock_listener = start_caps_lock_monitor()
    
    window = GastronomyApp()
    window.show()
    
    # Запускаем приложение
    exit_code = app.exec()
    
    # Останавливаем мониторинг при выходе
    if caps_lock_listener:
        caps_lock_listener.stop()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

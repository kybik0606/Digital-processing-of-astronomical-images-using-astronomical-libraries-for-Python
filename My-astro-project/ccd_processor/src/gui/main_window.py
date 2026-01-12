"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk
from .components.top_menu import TopMenu
from .components.stats_panel import StatsPanel
from .components.image_panel import ImagePanel
from .components.command_panel import CommandPanel
from .components.processing_panel import ProcessingPanel

class MainWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.setup_dark_theme()  # <-- Добавляем настройку темы
        self.setup_ui()
        
    def setup_dark_theme(self):
        """Настройка темной темы"""
        # Создаем стиль
        style = ttk.Style()
        
        # Устанавливаем темную цветовую схему
        self.root.configure(bg='#2b2b2b')
        
        # Настраиваем цвета для ttk виджетов
        style.theme_use('default')  # Используем стандартную тему как основу
        
        # Конфигурация цветов
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        select_bg = '#404040'
        select_fg = '#ffffff'
        entry_bg = '#3c3c3c'
        
        # Настраиваем стили для различных виджетов
        style.configure('.', 
                       background=bg_color,
                       foreground=fg_color,
                       fieldbackground=entry_bg)
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', 
                       background='#404040',
                       foreground=fg_color,
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        
        style.map('TButton',
                 background=[('active', '#505050')])
        
        style.configure('TEntry',
                       fieldbackground=entry_bg,
                       foreground=fg_color,
                       insertcolor=fg_color)
        
        style.configure('TCombobox',
                       fieldbackground=entry_bg,
                       background=bg_color,
                       foreground=fg_color,
                       arrowcolor=fg_color)
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', entry_bg)],
                 selectbackground=[('readonly', select_bg)],
                 selectforeground=[('readonly', select_fg)])
        
        # Настройка скроллбаров
        style.configure('Vertical.TScrollbar',
                       background=bg_color,
                       troughcolor='#3c3c3c',
                       arrowcolor=fg_color)
        
        style.configure('Horizontal.TScrollbar',
                       background=bg_color,
                       troughcolor='#3c3c3c',
                       arrowcolor=fg_color)
        
    def setup_ui(self):
        """Настройка главного интерфейса"""
        # Главный фрейм
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Применяем темный фон к главному фрейму
        self.main_frame.configure(style='TFrame')
        
        # Создаем компоненты
        self.top_menu = TopMenu(self.main_frame, self.app)
        self.stats_panel = StatsPanel(self.main_frame, self.app)
        self.image_panel = ImagePanel(self.main_frame, self.app)
        self.command_panel = CommandPanel(self.main_frame, self.app)
        self.processing_panel = ProcessingPanel(self.image_panel.frame, self.app)
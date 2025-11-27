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
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка главного интерфейса"""
        # Главный фрейм
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем компоненты
        self.top_menu = TopMenu(self.main_frame, self.app)
        self.stats_panel = StatsPanel(self.main_frame, self.app)
        self.image_panel = ImagePanel(self.main_frame, self.app)
        self.command_panel = CommandPanel(self.main_frame, self.app)
        self.processing_panel = ProcessingPanel(self.image_panel.frame, self.app)
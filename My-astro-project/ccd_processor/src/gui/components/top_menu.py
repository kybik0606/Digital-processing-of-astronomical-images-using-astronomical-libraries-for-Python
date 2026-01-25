"""
Верхнее меню приложения
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os

class TopMenu:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        """Создание верхнего меню"""
        self.menu_frame = ttk.Frame(self.parent)
        self.menu_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self._create_buttons()
        self._create_directory_selector()
        
    def _create_buttons(self):
        """Создание кнопок меню"""
        buttons = [
            ("Добавить Lights", self.app.add_lights),
            ("Добавить Darks", self.app.add_darks),
            ("Добавить Bias", self.app.add_bias),
            ("Добавить Flats", self.app.add_flats),
            ("Авто Flats", self.app.auto_flats)
        ]
        
        for text, command in buttons:
            ttk.Button(self.menu_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)
            
    def _create_directory_selector(self):
        """Создание селектора директории"""
        ttk.Button(self.menu_frame, text="Рабочая директория", 
                  command=self.app.set_working_directory).pack(side=tk.LEFT, padx=5)
        
        self.dir_label = ttk.Label(self.menu_frame, 
                                  text=f"Директория: {os.path.basename(self.app.working_directory)}")
        self.dir_label.pack(side=tk.LEFT, padx=0)